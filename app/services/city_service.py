from sqlalchemy.orm import Session

from app.models.db_models import City


DEFAULT_CITIES = (
    {
        "name": "Mumbai",
        "country": "India",
        "country_code": "IN",
        "timezone": "Asia/Kolkata",
        "latitude": 19.0760,
        "longitude": 72.8777,
    },
    {
        "name": "London",
        "country": "United Kingdom",
        "country_code": "GB",
        "timezone": "Europe/London",
        "latitude": 51.5074,
        "longitude": -0.1278,
    },
    {
        "name": "New York",
        "country": "United States",
        "country_code": "US",
        "timezone": "America/New_York",
        "latitude": 40.7128,
        "longitude": -74.0060,
    },
    {
        "name": "Tokyo",
        "country": "Japan",
        "country_code": "JP",
        "timezone": "Asia/Tokyo",
        "latitude": 35.6762,
        "longitude": 139.6503,
    },
    {
        "name": "Sydney",
        "country": "Australia",
        "country_code": "AU",
        "timezone": "Australia/Sydney",
        "latitude": -33.8688,
        "longitude": 151.2093,
    },
)


class CityService:
    @staticmethod
    def seed_default_cities(db: Session, reset_existing: bool = False) -> dict[str, int | str | bool]:
        if reset_existing:
            db.query(City).delete()
            db.commit()

        cities_created = 0
        for city_data in DEFAULT_CITIES:
            existing_city = (
                db.query(City)
                .filter(
                    City.name == city_data["name"],
                    City.country_code == city_data["country_code"],
                )
                .first()
            )
            if existing_city is not None:
                continue

            db.add(City(**city_data))
            cities_created += 1

        db.commit()

        total_active_cities = db.query(City).filter(City.is_active.is_(True)).count()
        message = (
            "Default cities seeded successfully."
            if cities_created > 0
            else "Default cities already available."
        )

        return {
            "success": True,
            "message": message,
            "cities_created": cities_created,
            "total_active_cities": total_active_cities,
        }

    @staticmethod
    def get_active_cities(db: Session) -> list[City]:
        return db.query(City).filter(City.is_active.is_(True)).order_by(City.name.asc()).all()

    @staticmethod
    def get_city_by_id(db: Session, city_id: int) -> City | None:
        return db.query(City).filter(City.id == city_id).first()
