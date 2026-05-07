import pathlib
import typer

from stones.weightdb import WeightDb


def migrate(dbpath: pathlib.Path) -> None:
    db = WeightDb(dbpath)
    db.create_table()


def main() -> None:
    typer.run(migrate)


if __name__ == "__main__":
    main()
