from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database
from app.models.db_models import PaperOrder, Position
from app.services.position_service import PositionService


def _session(tmp_path, monkeypatch):
    test_db_url = f"sqlite:///{tmp_path / 'position_service.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)
    database.init_db()

    return testing_session_local()


def _order(status: str = "paper_order_created", amount: float = 10.0, price: float = 0.5) -> PaperOrder:
    return PaperOrder(
        city_id=1,
        risk_report_id=1,
        prediction_id=1,
        market_snapshot_id=1,
        market_id="market-1",
        market_slug="market-1",
        side="YES",
        outcome="YES",
        requested_amount=amount,
        size=amount,
        notional_value=amount,
        simulated_price=price,
        status=status,
        paper_execution_source="local_simulation",
    )


def test_created_paper_order_creates_position(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        order = _order()
        db.add(order)
        db.flush()

        PositionService().update_position_from_order(db, order)

        assert db.query(Position).count() == 1
    finally:
        db.close()


def test_second_order_for_same_market_side_updates_existing_position(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        first = _order(amount=10.0, price=0.5)
        second = _order(amount=20.0, price=0.7)
        db.add_all([first, second])
        db.flush()

        service = PositionService()
        service.update_position_from_order(db, first)
        service.update_position_from_order(db, second)

        position = db.query(Position).first()
        assert db.query(Position).count() == 1
        assert position.total_size == 30.0
        assert position.total_cost == 30.0
    finally:
        db.close()


def test_skipped_paper_order_does_not_create_position(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        order = _order(status="paper_order_skipped", amount=0.0, price=0.0)
        db.add(order)
        db.flush()

        PositionService().update_position_from_order(db, order)

        assert db.query(Position).count() == 0
    finally:
        db.close()


def test_average_price_calculation_is_deterministic(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        first = _order(amount=10.0, price=0.5)
        second = _order(amount=30.0, price=0.8)
        db.add_all([first, second])
        db.flush()

        service = PositionService()
        service.update_position_from_order(db, first)
        service.update_position_from_order(db, second)

        assert db.query(Position).first().average_price == 1.0
    finally:
        db.close()


def test_position_values_are_simulated_and_non_negative(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        order = _order()
        db.add(order)
        db.flush()

        PositionService().update_position_from_order(db, order)
        position = db.query(Position).first()

        assert position.paper_execution_source == "local_simulation"
        assert position.total_size >= 0
        assert position.total_cost >= 0
        assert position.unrealized_pnl >= 0
    finally:
        db.close()
