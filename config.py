API_KEY = "ghfkffu6378382826hhdjgk"
BASE_URL = "https://bluemutualfund.in/server/api/company.php"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Replace with your real MySQL username/password/database
DB_URI = "mysql+mysqlconnector://root:Saijeevan@5689@localhost:3306/ml"

# SQLAlchemy Engine and Session
engine = create_engine(DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)