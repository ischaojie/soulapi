# soul-api
some datasets api

### version
- v1.0.0

    Hello SoulAPi !

### develop

default superuser login use:
```
email: admin@example.com
password: 123456
```

Fast run server:

```shell
# install all package
pipenv install
pipenv shell

# generate all db tables
python manage.py db create

# create default superuser with `--noinput`
python manage.py createsuper --noinput
# or just create a new superuser
# python manage.py createsuper

# run server in 127.0.0.1:8000
python manage.py run
```

use `python manage.py` for more detail.

### deploy in docker
```shell
cd soulapi

# change the docker-compose.yml for you

# start
docker-compose up -d
```

### TODO

- [ ] reset password support
- [ ] user profile can change
- [ ] superuser can add,update,delete user
- [x] daily psychology support
- [ ] add unit test