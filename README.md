# SoulAPI
SoulAPI 的初衷是给自己的电子日历
（ [Soul](https://githuv.com/shiniao/soul) ）
提供数据集支持，包括考研心理学知识点以及英语高频词汇。 后期会陆续扩充其他数据集。

### datasets
目前包含的数据集有：
- [x] 考研心理学知识点
- [x] 考研英语高频单词


### develop

默认的 superuser 账号：
```
email: admin@example.com
password: 123456
```

快速本地运行：

```shell
# 使用 pipenv 安装依赖包
pipenv install
# 激活虚拟环境
pipenv shell

# 生成数据库
python manage.py db create

# 创建默认 superuser
python manage.py createsuper --noinput
# 当然，也可以自定义

# run server in 127.0.0.1:8000
python manage.py run
```
访问 http://127.0.0.1:8000/docs 查看 api 详情。

另外，项目提供了方便的管理脚本支持，执行`python manage.py --help` 了解更多。

### deploy in docker
```shell
cd soulapi

# 根据自身需求修改 docker-compose.yml 配置

# start
docker-compose up -d
```

### TODO

- [x] reset password support
- [ ] user profile can change
- [x] superuser can read, add and update user
- [x] psychology support
- [x] english words support
- [x] add unit test


### version
- v1.0.0
    Hello SoulAPi !
    Psychologies knowledge and word api