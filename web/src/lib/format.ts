import { locale, t } from "./i18n";
import type { Report } from "./types";

export function childTitle(r: Report): string {
  return r.child_name || t("report.unnamed");
}

export function ageText(r: Pick<Report, "age">): string {
  return r.age === null ? t("age.unknown") : t("age.years", { n: r.age });
}

export function placeText(r: Pick<Report, "city" | "area">): string {
  return [r.area, r.city].filter(Boolean).join(locale.value === "ar" ? "، " : ", ");
}
