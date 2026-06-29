from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database
from app.models.db_models import MarketSnapshot
from app.services.city_service import CityService
from app.services.market_service import MarketService


def _session(tmp_path, monkeypatch):
    test_db_url = f"sqlite:///{tmp_path / 'market_service.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)
    database.init_db()

    return testing_session_local()


def test_refresh_markets_creates_mock_snapshots_for_mvp_cities(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        CityService.seed_default_cities(db)

        result = MarketService().refresh_markets(db)

        assert result == {
            "success": True,
            "cities_processed": 5,
            "market_snapshots_created": 5,
            "source_type": "mock",
            "fallback_used": True,
            "failed_markets": [],
            "pm_trader_enabled": False,
            "pm_trader_available": False,
            "readonly_mode": True,
            "order_execution_enabled": False,
        }
        snapshots = db.query(MarketSnapshot).all()
        assert len(snapshots) == 5
        assert {snapshot.source_type for snapshot in snapshots} == {"mock"}
        assert all(0 <= snapshot.yes_price <= 1 for snapshot in snapshots)
        assert all(0 <= snapshot.no_price <= 1 for snapshot in snapshots)
        assert all(0 <= snapshot.implied_probability <= 1 for snapshot in snapshots)
    finally:
        db.close()


def test_refresh_markets_uses_mock_fallback_when_pm_trader_disabled(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        CityService.seed_default_cities(db)

        result = MarketService().refresh_markets(db, force_mock=False, use_mock_if_unavailable=True)

        assert result["success"] is True
        assert result["market_snapshots_created"] == 5
        assert result["source_type"] == "mock"
        assert result["fallback_used"] is True
        assert result["pm_trader_enabled"] is False
        assert result["pm_trader_available"] is False
        assert result["readonly_mode"] is True
        assert result["order_execution_enabled"] is False
    finally:
        db.close()


def test_get_markets_returns_records(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        CityService.seed_default_cities(db)
        service = MarketService()
        service.refresh_markets(db)

        records = service.get_markets(db)

        assert records
        assert len(records) == 5
    finally:
        db.close()


def test_refresh_markets_city_ids_filter_works(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        CityService.seed_default_cities(db)
        city = CityService.get_active_cities(db)[0]

        result = MarketService().refresh_markets(db, city_ids=[city.id])

        assert result["cities_processed"] == 1
        assert result["market_snapshots_created"] == 1
        records = MarketService().get_markets(db, city_id=city.id)
        assert len(records) == 1
        assert records[0].city_id == city.id
    finally:
        db.close()
