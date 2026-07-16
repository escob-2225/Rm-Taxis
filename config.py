class Config:
    SECRET_KEY = "TuClaveSuperSegura123"

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/taxi_manager"

    SQLALCHEMY_TRACK_MODIFICATIONS = False