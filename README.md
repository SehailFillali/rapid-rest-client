REST-CLIENT
===========

Setup a client in minutes

---

### Installation

````bash
pip install rapid-rest-client
````

### Usage

There are multiple options to auto-create a client. Here's using a swagger definition:

````python
from rest_client.base import BaseUrlConfig, SwaggerApiConfiguration, Client

petstore_endpoint_config: BaseUrlConfig = BaseUrlConfig('https://petstore.swagger.io/v2/')

@SwaggerApiConfiguration(url='https://petstore.swagger.io/v2/swagger.json', base_url_config=petstore_endpoint_config)
class SwaggerUrlConfiguredClient(Client):
    pass

swagger_url_configured_client = SwaggerUrlConfiguredClient()

# Client now has all paths available, as defined in the json file at url

r = swagger_url_configured_client.find_pets_by_status(status='pending')
print(r)
````

You can also pass the swagger definition as a dict:

````python

@SwaggerApiConfiguration(definition={<swagger dict>}, base_url_config=petstore_endpoint_config)

````

Manually creating a client:

```python
from rest_client.base import BaseUrlConfig, ApiConfiguration, RequestConfig, Client

endpoint_config: BaseUrlConfig = BaseUrlConfig('https://reqres.in/api/', 'https://sandbox.reqres.in/api/')

@ApiConfiguration(endpoints=[
    RequestConfig('users', 'list_users'),
    RequestConfig('users/{}', 'get_user'),
    RequestConfig('register', 'register_user', 'POST')
], base_url_config=endpoint_config)
class ExampleClient(Client):
    pass

```

This makes these methods available on `ExampleClient`

- list_users
- get_user 
- register_user

```python
client = ExampleClient()
list_users_response = client.list_users()
get_user_response = client.get_user(3)
register_user_response = client.register_user(email="eve.holt@reqres.in", password="pistol")
```

If you want to customize a method, you can simply add methods to a client. Use the `endpoint` decorator to do that:

```python
from rest_client.base import endpoint, Client

class ExampleClient(Client):
    @endpoint('users', 'list_users')
    def list_users(self, **kwargs):
        return self._request(kwargs)

```

You can also create the client from json, or a dict:

````python
from rest_client.base import DictApiConfiguration, BaseUrlConfig, Client

endpoint_config: BaseUrlConfig = BaseUrlConfig('https://reqres.in/api/')

@DictApiConfiguration(endpoints=[{
    'path': 'users',
    'name': 'list_users',
}], base_url_config=endpoint_config)
class MyClient(Client):
    pass
````

### Authentication

You can pass custom authentication through the `authentication_handler` property. Authentication handlers should extend AuthBase from `requests.auth`

For example: 

```python
from rest_client.base import BaseUrlConfig, ApiConfiguration, RequestConfig, Client, BearerTokenAuth

auth_endpoint_config: BaseUrlConfig = BaseUrlConfig('https://gorest.co.in/public/v1/')

@ApiConfiguration(
    endpoints=[
        RequestConfig('users', 'register_user', 'POST'),
    ],
    base_url_config=auth_endpoint_config)
class AuthClient(Client):
    pass

auth_client = AuthClient(
    authentication_handler=BearerTokenAuth('token')
)
```

---

Please note:

This is a work in progress and completely new. Contributions are very welcome. 

---
