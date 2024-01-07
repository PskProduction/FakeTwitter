from environs import Env

env = Env()
env.read_env()

DB_USER: str = env.str("DB_USER")
DB_PASS: str = env.str("DB_PASS")
DB_HOST: str = env.str("DB_HOST")
DB_PORT: str = env.str("DB_PORT")
DB_NAME: str = env.str("DB_NAME")
