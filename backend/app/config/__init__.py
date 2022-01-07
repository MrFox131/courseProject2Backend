import os

db_host = os.getenv("POSTGRES_HOST", default="127.0.0.1")
db_port = ":" + os.getenv("DB_PORT", default="")
if db_port == ":":
    db_port = ""

db_user = os.getenv("DB_USER", default="postgres")
db_pass = os.getenv("POSTGRES_PASSWORD", default="postgres")

db = os.getenv("POSTGRES_DB", "courseProject")

db_url = f"postgresql://{db_user}:{db_pass}@{db_host}{db_port}/courseProject"
