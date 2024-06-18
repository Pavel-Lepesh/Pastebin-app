function secondHello(r) {
    r.return(200, r.uri)
}

function handleSignup(r) {
    try {
        var body = JSON.parse(r.requestBuffer);
    } catch (e) {
        r.return(400, JSON.stringify({ error: "Invalid JSON in request body" }));
        return;
    }
    var username = body.username;
    var password = body.password;
    var email = body.email;

    if (!username || !password || !email) {
        r.return(400, JSON.stringify({ error: "Missing required fields: username, password, email" }));
        return;
    }

    var auth_body = JSON.stringify({
        username: username,
        password: password,
        email: email
    });

    r.subrequest('/_subrequest_auth', {
        method: 'POST',
        body: auth_body
    }, function(reply) {
        if (reply.status == 201) {
            var tokens = JSON.parse(reply.responseBuffer);
            var access_token = tokens.access_token;
            var refresh_token = tokens.refresh_token;
            var user_id = tokens.id;

            r.headersOut['Authorization'] = access_token;
            r.headersOut['X-Refresh-Token'] = refresh_token;
            r.headersOut['Set-Cookie'] = `pastebin_refresh_token=${refresh_token}; HttpOnly`;

            body.id = user_id;
            var updated_request_body = JSON.stringify(body);

            r.subrequest('/_proxy_to_pastebin_signup', {
                method: r.method,
                body: updated_request_body,
                headers: r.headersIn
            }, function(proxy_reply) {
                r.return(proxy_reply.status, proxy_reply.responseBuffer);
            });
        } else {
            r.return(500, reply.status);
        }
    });
}

function handleDeleteUser(r) {
    var authHeader = r.headersIn['Authorization'];
    var request_body = JSON.stringify({
        access_token: authHeader
    });
    
    r.subrequest('/_self_delete_user', {
        method: 'DELETE',
        body: request_body
    }, function(reply) {
        if (reply.status == 204) {
            r.subrequest('/_proxy_to_pastebin_delete_user', {
                method: r.method,
                headers: r.headersIn
            }, function(proxy_reply) {
                r.return(proxy_reply.status, proxy_reply.responseBuffer);
            });
        } else {
            r.return(reply.status, reply.responseBuffer);
        }
    });
}

function authStage(r) {
    var authHeader = r.headersIn['Authorization'];

    if (!authHeader) {
        r.return(400, JSON.stringify({ error: "Authorization header is required" }));
        return;
    }
    var auth_body = JSON.stringify({
        access_token: authHeader
    });
    r.subrequest('/_subrequest_verify_token', {
        method: 'POST',
        body: auth_body
    }, function(reply) {
        if (reply.status == 200) {
             r.headersOut['Authorization'] = authHeader;

             var requestBody = '';
             try {
                 requestBody = JSON.stringify(JSON.parse(r.requestBuffer));
             } catch (e) {
                 requestBody = '';
             }

             r.subrequest("/_proxy_to_main_service", {
                method: r.method,
                body: requestBody,
                headers: r.headersIn
             }, function(proxy_reply) {
                r.return(proxy_reply.status, proxy_reply.responseBuffer);
             })
        } else {
            r.log(`Subrequest status: ${reply.status}, Subrequest responseText: ${reply.responseText}`);
            // r.return(reply.status, reply.responseText);

            // Get pastebin_refresh_token from cookies
            var cookies = r.headersIn['Cookie'];
            var refreshToken = '';
            if (cookies) {
                var cookieArray = cookies.split(';');
                for (var i = 0; i < cookieArray.length; i++) {
                    var cookie = cookieArray[i].trim();
                    if (cookie.startsWith('pastebin_refresh_token=')) {
                        refreshToken = cookie.substring('pastebin_refresh_token='.length);
                        break;
                    }
                }
            }

            if (!refreshToken) {
                r.return(400, JSON.stringify({ error: "pastebin_refresh_token cookie is required" }));
                return;
            }

            var auth_refresh_body = JSON.stringify({
                refresh_token: refreshToken
             });

            r.subrequest("/_subrequest_refresh_token", {
                method: 'POST',
                body: auth_refresh_body
            }, function(reply) {
                if (reply.status == 200) {
                    var new_tokens = JSON.parse(reply.responseBuffer);
                    var access_token = new_tokens.access_token;
                    var refresh_token = new_tokens.refresh_token

                    r.headersOut['Set-Cookie'] = `pastebin_refresh_token=${refresh_token}; Path=/; HttpOnly`;
                    r.headersOut['New access token'] = access_token;

                    r.return(200, 'it is necessary to replace the access token')
                } else {
                    r.return(reply.status, reply.responseBuffer);
                }
            })
        }
    });
}

export default { secondHello, handleSignup, authStage, handleDeleteUser };