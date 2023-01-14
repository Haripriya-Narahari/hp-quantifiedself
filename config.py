import os
#bdir = os.path.abspath(os.path.dirname(__file__))
class Config():
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    SECURITY_TOKEN_AUNTHENTICATION_HEADER = "Authentication-Token"
    CELERY_BROKER_URL = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
    REDIS_URL = "redis://localhost:6379/3"
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = "6379"

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.sqlite3"
    SECRET_KEY =os.environ.get("Secret Key","qsqhj1g3h26")
    SECURITY_PASSWORD_SALT = os.environ.get("Security Password Salt","1221723151422")
    WTF_CSRF_ENABLED = False
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_USERNAME_ENABLE = True
    CORS_HEADERS = 'Content-Type'
    CORS_ORIGINS = "*"
    CORS_RESOURCES = r"/*"
    CELERY_BROKER_URL = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
    CELERY_ENABLED= True
    REDIS_URL = "redis://localhost:6379/3"
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = "6379"
    
    
    
