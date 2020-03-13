import pymysql
from mysite.celery import app as celery_app

pymysql.install_as_MySQLdb()
# 通常只到这里截止，现在为了伪装版本，加入下一句代码
pymysql.version_info = (1, 3, 13, "final", 0)
