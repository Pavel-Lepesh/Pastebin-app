# Pastebin application
___
<a href="https://www.postman.com/pavellepesh/workspace/pastebin/collection/26749338-970d2184-c825-4347-a8fe-32fa70906536"><img src="https://img.shields.io/badge/Postman-pastebin collection-orange"></a>
## Описание 
___
Этот проект представляет собой веб-приложение, созданное для публикации
текстовых фрагментов. Фрагменты могут иметь как приватный доступ, так и
публичный. Дополнительно имеется возможность выбора времени жизни вашего 
фрагмента.

## Архитектура приложения
___
Ниже приведена графическая схема архитектуры приложения:
![Схема архитектуры приложения](pastebin-schema.png)
### Составляющие приложения:
* __Основной сервис__, написанный на Django/Django Rest Framework. Здесь
происходит большая часть взаимодействий между сервисами;
* __Сервис аутентификации__, написанный на FastAPI. Используется для регистрации пользователей 
и их аутентификации и авторизации посредством выдачи JWT токенов. Основное 
взаимодействие происходит за счет автоматических подзапросов к этому сервису через nginx
в момент обычных запросов пользователей к основному приложению;
* __Nginx__. Выполняет роль маршрутизатора запросов и распределителя нагрузки на сервис. 
Также отвечает за взаимодействие с сервисом аутентификации;
* __Сервис генерации хэшей__, написанный на FastAPI. Используется для получения хэш-ссылок, которые в 
дальнейшем будут использоваться в url-адресах для доступа к записям пользователей;
  * __Redis__. Используется в качестве временного хранилища хэш-ссылок для быстрого доступа к ним из RabbitMQ;
  * __RabbitMQ__. Используется в качестве брокера сообщений для передачи хэш-ссылок из
  сервиса генерации хэшей в основной сервис;
* __PostgreSQL__. Основная база данных приложения;
* __Memcached__. Кэш, который используется для хранения популярных записей пользователей;
* __S3 Storage__. Хранилище, в котором сохраняются все записи пользователей;
* __Celery__. Асинхронная очередь задач, через которую происходит удаление мета-данный устаревших записей. 
Опционально, может использоваться также для удаления записей из S3 хранилища, если оно не поддерживает 
автоматическое удаление записей по истечении срока жизни фрагментов.

## Особенности работы приложения
___
>Приложение разработано по принципу микросервисной архитектуры и свободно для масштабирования. 
[__Генератор хешей__](https://github.com/Pavel-Lepesh/Pastebin-hash-generator) и [__Сервис аутентификации__](https://github.com/Pavel-Lepesh/Pastebin-authentication-service) 
являются универсальными приложениями, они так 
же могут использоваться в других проектах.

Пользователям предоставляется доступ к операциям создания и управления своими записями, а также для просмотра
популярных публичных записей других пользователей. Есть возможность добавления понравившихся записей к себе в "My stars".
Реализованы системы комментариев и рейтинга записей и комментариев. 

>Документация API приложения доступна [здесь](https://www.postman.com/pavellepesh/workspace/pastebin/collection/26749338-970d2184-c825-4347-a8fe-32fa70906536).
