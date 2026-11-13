// Arabic by default (text in the HTML), English on toggle; dark by default, light on toggle.
(function () {
  var en = {
    "name": "Ana Fein?",
    "nav.how": "How it works", "nav.features": "Features", "nav.screens": "Inside the app", "nav.privacy": "Privacy",
    "hero.eyebrow": "A free community platform",
    "hero.title": "Every missing-child report meets the report of a child someone found",
    "hero.lead": "Post a report with photos in a minute. The platform compares missing reports with found reports automatically and alerts the family and the finder at the same moment.",
    "video.title": "See Ana Fein in action",
    "hero.cta": "See the app", "hero.cta2": "How it works",
    "hero.t1": "Missing or found reports with photos",
    "hero.t2": "Automatic matching by age, place and date",
    "hero.t3": "Private photos, shown only through short-lived links",
    "how.title": "Three steps",
    "how.s1": "Report", "how.s1p": "Choose \"a child is missing\" or \"I found a child\", describe the child, the place and the date, and add photos from your phone.",
    "how.s2": "Match", "how.s2p": "Each report is compared with the open reports of the other kind: gender, age over time, distance, dates and photos.",
    "how.s3": "Reunite", "how.s3p": "Both sides get notified, compare the two reports side by side, confirm the match and talk in private messages.",
    "f.title": "Everything needed to bring a child home",
    "f.1": "Reports with photos", "f.1p": "Up to 6 photos per report, uploaded straight from the device to secure storage, with a progress bar.",
    "f.2": "Automatic matching", "f.2p": "A score out of 100 with clear reasons: same gender, matching age, under 5 km apart, close dates.",
    "f.3": "Search and filters", "f.3p": "Search by name, description or area, and filter by gender, age, city and report status.",
    "f.4": "Private messages", "f.4p": "Talk to the reporter directly and send an image or a PDF safely.",
    "f.5": "Notifications", "f.5p": "New match, comment, support or message: all in one place.",
    "f.6": "A community that cares", "f.6p": "Comments, support and link sharing so a report reaches as many people as possible.",
    "f.7": "Moderation and safety", "f.7p": "Anyone can flag a suspicious report; moderators review and hide false ones.",
    "f.8": "Arabic and English, dark and light", "f.8p": "Right-to-left Arabic, English in one tap, dark or light mode, and it works on phones.",
    "s.title": "Inside the app",
    "s.report": "Report page", "s.matches": "Matches", "s.new": "New report", "s.search": "Search",
    "s.messages": "Messages", "s.notifications": "Notifications", "s.admin": "Moderation",
    "s.cap.report": "The report page: photos, details, support and comments, the reporter's tools and possible matches.",
    "s.cap.matches": "Suggested matches side by side with a score and the reasons; both reporters can confirm or dismiss.",
    "s.cap.new-report": "A new report: type, child details, place and date, and photos uploaded directly to storage.",
    "s.cap.search": "Search and filters: missing or found, gender, age range, city and free text.",
    "s.cap.messages": "Private messages between families and finders, with image and PDF attachments.",
    "s.cap.notifications": "Notifications for matches, comments, support and messages.",
    "s.cap.admin": "Moderation: flagged reports, hidden reports and user management.",
    "p.title": "Children's privacy first",
    "p.1": "Photos live in private storage; no photo has a permanent link.",
    "p.2": "Every photo is shown through a temporary link that expires within minutes.",
    "p.3": "The contact number is visible to signed-in users only.",
    "p.4": "The type and size of every file are checked; a file that breaks the rules is deleted at once.",
    "p.5": "Suspicious reports are hidden until a moderator reviews them.",
    "c.title": "Every share could bring a child home",
    "c.lead": "Free for families, volunteers and community organisations.",
    "foot.demo": "Every name and picture in the screenshots is generated demo data and does not belong to real children."
  };
  var arCaps = {
    "report": "صفحة البلاغ: الصور، التفاصيل، التضامن والتعليقات، وأدوات صاحب البلاغ والتطابقات المحتملة.",
    "matches": "التطابقات المقترحة جنبًا إلى جنب مع الدرجة والأسباب، ولكل طرف أن يؤكد أو يستبعد.",
    "new-report": "بلاغ جديد: النوع، بيانات الطفل، المكان والتاريخ، والصور تُرفع مباشرة للتخزين.",
    "search": "البحث والفلاتر: مفقود أو معثور عليه، النوع، العمر، المدينة، ونص حر.",
    "messages": "رسائل خاصة بين الأسر ومن عثروا على الأطفال، مع إرفاق صور وملفات PDF.",
    "notifications": "إشعارات بالتطابقات والتعليقات والتضامن والرسائل.",
    "admin": "الإشراف: البلاغات عليها ملاحظات، البلاغات المخفية، وإدارة المستخدمين."
  };
  var root = document.documentElement;
  var nodes = document.querySelectorAll("[data-i18n]");
  var ar = {};
  nodes.forEach(function (n) { ar[n.getAttribute("data-i18n")] = n.textContent; });
  var current = "report";

  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function isEn() { return root.lang === "en"; }
  function isLight() { return root.dataset.theme === "light"; }

  function shot(name) {
    if (isLight() && (name === "report")) return "assets/screens/report-light.png";
    return "assets/screens/" + name + ".png";
  }

  function render() {
    var dict = isEn() ? en : ar;
    nodes.forEach(function (n) { var k = n.getAttribute("data-i18n"); if (dict[k]) n.textContent = dict[k]; });
    document.getElementById("lang").textContent = isEn() ? "العربية" : "English";
    document.getElementById("theme").textContent = isLight() ? "☾" : "☀";
    var hero = document.querySelector(".hero-shot .shot");
    hero.src = "assets/screens/home-" + (isEn() ? "en" : "ar") + "-" + (isLight() ? "light" : "dark") + ".png";
    document.querySelector(".hero-shot .phone").src = "assets/screens/mobile-home" + (isEn() ? "-en" : "") + ".png";
    document.getElementById("viewer").src = shot(current);
    document.getElementById("caption").textContent = isEn() ? en["s.cap." + current] : arCaps[current];
    document.title = isEn() ? "Ana Fein? — missing children reports" : "أنا فين؟ — منصة بلاغات الأطفال المفقودين";
  }

  document.getElementById("lang").addEventListener("click", function () {
    var toEn = !isEn();
    root.lang = toEn ? "en" : "ar";
    root.dir = toEn ? "ltr" : "rtl";
    store("site-locale", root.lang);
    render();
  });
  document.getElementById("theme").addEventListener("click", function () {
    root.dataset.theme = isLight() ? "dark" : "light";
    store("site-theme", root.dataset.theme);
    render();
  });
  document.querySelectorAll(".tab").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll(".tab").forEach(function (x) { x.classList.remove("on"); });
      b.classList.add("on");
      current = b.dataset.shot;
      render();
    });
  });
  render();
})();
