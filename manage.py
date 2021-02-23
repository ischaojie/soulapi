import typer
import uvicorn
from alembic.config import Config

import alembic
from app import crud, schemas
from app.database import SessionLocal

app = typer.Typer()


@app.command()
def run(
    host: str = typer.Option("127.0.0.1", help="server host"),
    port: int = typer.Option(8000, help="server port"),
    log_level: str = typer.Option("info", "--log-level", help="log level"),
    reload: bool = typer.Option(True, help="whether auto reload"),
):
    uvicorn.run(
        "app.main:app", host=host, port=port, log_level=log_level, reload=reload
    )


@app.command()
def createsuperuser():
    username = typer.prompt("username:", default="admin")
    email = typer.prompt("email:", default="admin@example.com")
    password = typer.prompt("password:")

    db = SessionLocal()
    superuser = schemas.UserCreate(
        full_name=username,
        email=email,
        password=password,
    )
    user_db = crud.user.create_superuser(db, obj=superuser)
    typer.echo("superuser created.")


# db command

db_app = typer.Typer()

alembic_cfg = Config("alembic.ini")


@db_app.command("init")
def db_init(name: str = "alembic"):
    alembic.command.init(alembic_cfg, name)


@db_app.command("migration")
def db_migration(message: str = typer.Option("", "-m", help="message for migration")):
    alembic.command.revision(alembic_cfg, message=message, autogenerate=True)


@db_app.command("upgrade")
def db_upgrade():
    alembic.command.upgrade(alembic_cfg, revision="head")


app.add_typer(db_app, name="db")

if __name__ == "__main__":
    app()
