from src.db.base import Base
from src.db.session import engine
import src.db.models  # noqa

def main():
    Base.metadata.create_all(bind=engine)
    print("Database initialized")

if __name__ == "__main__":
    main()
