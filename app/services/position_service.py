from sqlalchemy.orm import Session

from app.models.db_models import PaperOrder, Position


class PositionService:
    def update_position_from_order(self, db: Session, paper_order: PaperOrder) -> dict:
        if paper_order.status != "paper_order_created":
            return {"success": True, "position_updated": False, "position_id": None}

        existing_position = (
            db.query(Position)
            .filter(
                Position.market_slug == paper_order.market_slug,
                Position.side == paper_order.side,
            )
            .first()
        )
        order_size = paper_order.size or paper_order.requested_amount or 0.0
        notional_value = paper_order.notional_value or paper_order.requested_amount or 0.0
        simulated_price = paper_order.simulated_price or 0.0

        if existing_position is None:
            existing_position = Position(
                city_id=paper_order.city_id,
                market_id=paper_order.market_id,
                market_slug=paper_order.market_slug,
                side=paper_order.side,
                outcome=paper_order.outcome,
                total_size=0.0,
                average_price=0.0,
                total_cost=0.0,
                current_price=simulated_price,
                current_market_price=simulated_price,
                unrealized_pnl=0.0,
                realized_pnl=0.0,
                paper_execution_source=paper_order.paper_execution_source,
                status="open",
            )
            db.add(existing_position)

        existing_position.total_size = (existing_position.total_size or 0.0) + order_size
        existing_position.total_cost = (existing_position.total_cost or 0.0) + notional_value
        existing_position.average_price = (
            existing_position.total_cost / existing_position.total_size
            if existing_position.total_size > 0
            else 0.0
        )
        existing_position.current_price = simulated_price
        existing_position.current_market_price = simulated_price
        existing_position.unrealized_pnl = 0.0
        existing_position.status = "open"
        db.flush()
        return {"success": True, "position_updated": True, "position_id": existing_position.id}

    def get_positions(
        self,
        db: Session,
        city_id: int | None = None,
        status: str | None = None,
    ) -> list[Position]:
        query = db.query(Position)
        if city_id is not None:
            query = query.filter(Position.city_id == city_id)
        if status is not None:
            query = query.filter(Position.status == status)
        return query.order_by(Position.updated_at.desc(), Position.id.desc()).all()
