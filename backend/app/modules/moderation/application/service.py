from uuid import UUID, uuid4

from app.modules.moderation.domain.flag import Flag, FlagRepository, check_reason, should_auto_hide
from app.modules.reports import Report, ReportsService
from app.shared.domain.errors import Conflict
from app.shared.domain.paging import PageRequest
from app.shared.domain.principal import Principal

AUTO_HIDE_REASON = "auto: flagged by several users, waiting for review"


class ModerationService:
    def __init__(self, flags: FlagRepository, reports: ReportsService) -> None:
        self.flags, self.reports = flags, reports

    def flag(self, who: Principal, report_id: UUID, reason: str, note: str | None) -> bool:
        """Returns True when the report was hidden automatically."""
        report = self.reports.get(who, report_id)
        reason, note = check_reason(reason, note)
        if self.flags.has_open(report.id, who.user_id):
            raise Conflict("You already flagged this report", "already_flagged")
        self.flags.add(Flag(uuid4(), report.id, who.user_id, reason, note))
        if should_auto_hide(self.flags.open_count(report.id), report.status == "hidden"):
            self.reports.hide(report.id, AUTO_HIDE_REASON)
            return True
        return False

    def queue(self, page: PageRequest) -> tuple[list[tuple[Report, int, list[str]]], int]:
        rows, total = self.flags.queue(page.offset, page.per_page)
        out = []
        for report_id, count, reasons in rows:
            r = self.reports.snapshot(report_id)
            if r:
                out.append((r, count, reasons))
        return out, total

    def hide(self, report_id: UUID, reason: str) -> Report:
        report = self.reports.hide(report_id, reason)
        self.flags.close_for_report(report_id)
        return report

    def restore(self, report_id: UUID) -> Report:
        report = self.reports.unhide(report_id)
        self.flags.close_for_report(report_id)
        return report

    def dismiss_flags(self, report_id: UUID) -> int:
        return self.flags.close_for_report(report_id)
