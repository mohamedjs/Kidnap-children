from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import array_agg
from sqlalchemy.orm import Session

from app.modules.moderation.domain.flag import OPEN, Flag, FlagRepository
from app.modules.moderation.infrastructure.models import FlagRow


class SqlFlagRepository(FlagRepository):
    def __init__(self, session: Session) -> None:
        self.s = session

    def add(self, flag: Flag) -> None:
        self.s.add(FlagRow(id=flag.id, report_id=flag.report_id, reporter_id=flag.reporter_id, reason=flag.reason,
                           note=flag.note, status=flag.status))
        self.s.flush()

    def has_open(self, report_id: UUID, reporter_id: UUID) -> bool:
        return self.s.scalar(select(func.count()).select_from(FlagRow).where(
            FlagRow.report_id == report_id, FlagRow.reporter_id == reporter_id, FlagRow.status == OPEN)) != 0

    def open_count(self, report_id: UUID) -> int:
        return self.s.scalar(select(func.count(func.distinct(FlagRow.reporter_id))).where(
            FlagRow.report_id == report_id, FlagRow.status == OPEN)) or 0

    def queue(self, offset: int, limit: int) -> tuple[list[tuple[UUID, int, list[str]]], int]:
        grouped = (select(FlagRow.report_id, func.count().label("n"), array_agg(FlagRow.reason).label("reasons"),
                          func.max(FlagRow.created_at).label("last"))
                   .where(FlagRow.status == OPEN).group_by(FlagRow.report_id))
        total = self.s.scalar(select(func.count()).select_from(grouped.subquery())) or 0
        rows = self.s.execute(grouped.order_by(func.count().desc(), func.max(FlagRow.created_at).desc())
                              .offset(offset).limit(limit)).all()
        return [(r.report_id, int(r.n), sorted(set(r.reasons))) for r in rows], total

    def close_for_report(self, report_id: UUID) -> int:
        res = self.s.execute(update(FlagRow).where(FlagRow.report_id == report_id, FlagRow.status == OPEN)
                             .values(status="closed"))
        return int(getattr(res, "rowcount", 0) or 0)
