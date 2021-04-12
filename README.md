## python 环境

请使用conda创建新的环境

```bash
conda env create -f .\environment.yml
```

## 在 docker 中部署(推荐)
1.  获取`docker pull xdcat/centos:ponsol2`
2.  运行`docker run -tid -p8091:3306 -p8090:80 --name ponsol2 --privileged=true xdcat/centos:ponsol2 /usr/sbin/init`
3. 网站将会在8090端口运行

## 在 linux 上部署(uwsgi)

1. 使用 conda 创建新的环境，如上所示
2. 迁移数据库
    * 修改数据库配置：
        * db.config 实际环境
        * db_dev.config 开发环境
    * 使用 makemigrations 和 migrate 迁移数据
2. 确保项目能够正常运行

    ```bash
    python manage.py runserver
    ```

3. 使用 uwsgi 部署
    * 安装 uwsgi
        ```bash
        pip install uwsgi --upgrade   
        ```
        
    * 迁移静态文件
        * 修改迁移后路径，在setting.py中修改
             ```python
             STATIC_ROOT = '/srv/django/ponsol2/static'
             ```
        * 迁移
            ```bash
            python ./manage.py collectstatic
            ```
        
    * 修改配置文件
        * 将 setting.py 的 `DEBUG` 修改为 `False`
        * 修改 uwsgi.ini 的 `chdir` 和 `static-map`(迁移后路径)
        
* 运行
   ```bash
   nohup /root/anaconda3/bin/uwsgi --ini /root/box/Ponsol_Web/uwsgi.ini > run_ponsol2_uwsgi.log 2>&1 &
   ```
       

