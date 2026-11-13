// Fills the dev app with realistic content THROUGH THE UI: each person signs up on /register,
// logs in, posts their report with photos (presigned upload), and others comment and like.
// Photos are AI-generated portraits of fictional children (video/photos, see genphoto.py).
//   node video/populate.mjs        (needs the dev stack; accounts use the test password in .env)
import fs from "node:fs";
import path from "node:path";
import { launch, demoPassword, WEB } from "../web/scripts/browser.mjs";

const HERE = import.meta.dirname;
const ph = (f) => path.join(HERE, "photos", f);
const ago = (d) => new Date(Date.now() - d * 864e5).toISOString().slice(0, 10);
const PASS = demoPassword();

const PEOPLE = {
  mona:  { name: "منى سالم",   email: "mona.salem@example.com",  phone: "+20 100 000 0101", city: "القاهرة" },
  tarek: { name: "طارق حسن",   email: "tarek.hassan@example.com", phone: "+20 100 000 0102", city: "الجيزة" },
  sara:  { name: "سارة مجدي",  email: "sara.magdy@example.com",   phone: "+20 100 000 0104", city: "الإسكندرية" },
  omar:  { name: "عمر حسين",   email: "omar.hussein@example.com", phone: "+20 100 000 0105", city: "المنصورة" },
  karim: { name: "كريم عادل",  email: "karim.adel@example.com",   phone: "+20 100 000 0106", city: "الجيزة" },
  nour:  { name: "نور الدين",  email: "nour.eldin@example.com",   phone: "+20 100 000 0107", city: "الإسكندرية" },
  heba:  { name: "هبة فاروق",  email: "heba.farouk@example.com",  phone: "+20 100 000 0103", city: "القاهرة" },
};

const REPORTS = [
  { who: "mona", kind: "missing", child: "يوسف", gender: "male", age: 6, date: ago(3), city: "القاهرة", area: "شبرا", geo: [30.0711, 31.2459],
    photos: ["youssef-1.jpg", "youssef-2.jpg"],
    desc: "يوسف خرج من المدرسة يوم الاتنين الساعة ٢ الضهر وما رجعش البيت. لابس سويتر أزرق تريكو وبنطلون جينز وشنطة ضهر ملونة. بيعرف اسمه واسم باباه. أي حد يشوفه يكلمنا فورًا." },
  { who: "tarek", kind: "missing", child: "مريم", gender: "female", age: 9, date: ago(5), city: "الجيزة", area: "الهرم", geo: [29.9870, 31.1310],
    photos: ["mariam-1.jpg"],
    desc: "مريم تاهت مننا في سوق الهرم بالليل. شعرها طويل ومربوط ديل حصان، لابسة فستان بمبي وشنطة ضهر بنفسجي. بتتكلم كويس وتعرف عنوان البيت." },
  { who: "sara", kind: "missing", child: "آدم", gender: "male", age: 4, date: ago(2), city: "الإسكندرية", area: "سموحة", geo: [31.2156, 29.9553],
    photos: ["adam-1.jpg"],
    desc: "آدم اتفقد في حديقة سموحة يوم الجمعة العصر. شعره كيرلي فاتح، لابس تيشيرت أصفر. صغير وبيتكلم قليل، بيعرف اسمه واسم مامته بس." },
  { who: "omar", kind: "missing", child: "ليلى", gender: "female", age: 12, date: ago(8), city: "المنصورة", area: "توريل", geo: [31.0409, 31.3785],
    photos: ["laila-1.jpg"],
    desc: "ليلى ما رجعتش من الدرس الخصوصي. لابسة نضارة طبية وجاكيت أخضر وشعرها ضفيرة. معاها موبايل بس مقفول من ساعتها." },
  { who: "karim", kind: "found", child: "تقول اسمها مريم", gender: "female", age: 9, date: ago(4), city: "الجيزة", area: "فيصل", geo: [30.0010, 31.1500],
    photos: ["mariam-found.jpg"],
    desc: "لقينا بنت تايهة في شارع فيصل، بتقول اسمها مريم وإنها من الهرم. لابسة فستان بمبي. هي دلوقتي في قسم الطالبية ومعاها أمينة شرطة." },
  { who: "nour", kind: "found", child: "", gender: "female", age: 3, date: ago(1), city: "الإسكندرية", area: "محرم بك", geo: [31.1950, 29.9200],
    photos: ["found-girl-alex.jpg"],
    desc: "طفلة صغيرة حوالي ٣ سنين لقيناها قدام المحل عندنا في محرم بك، لابسة جاكيت أحمر. مش قادرة تقول اسم أهلها. موجودة معانا في أمان." },
];

const COMMENTS = [
  { who: "sara", on: 0, text: "ربنا يرجعهولك بالسلامة يا رب. شيّرت البوست في جروبات شبرا." },
  { who: "karim", on: 0, text: "هسأل في محطة روض الفرج، الأمن هناك بيلاقوا أطفال كتير." },
  { who: "omar", on: 1, text: "في بلاغ عثور في فيصل لبنت اسمها مريم، بصّوا على التطابقات." },
  { who: "mona", on: 2, text: "ربنا يطمّن قلبك، إن شاء الله يرجع النهارده." },
  { who: "tarek", on: 5, text: "ربنا يجازيكم خير إنكم خليتوها معاكم في أمان." },
];
const LIKES = { 0: ["sara", "karim", "omar", "tarek"], 1: ["mona", "karim"], 2: ["mona", "omar"], 3: ["sara"], 5: ["tarek", "mona"] };

const browser = await launch();
async function as(who, geo, fn) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, locale: "ar-EG",
    geolocation: geo ? { latitude: geo[0], longitude: geo[1] } : undefined, permissions: geo ? ["geolocation"] : [] });
  const p = await ctx.newPage();
  await p.goto(`${WEB}/login`);
  await p.fill('input[type="email"]', PEOPLE[who].email);
  await p.fill('input[type="password"]', PASS);
  await p.click("button.btn.primary");
  await p.waitForURL(`${WEB}/`);
  try { return await fn(p); } finally { await ctx.close(); }
}

// 1. sign up everyone through /register
for (const [who, u] of Object.entries(PEOPLE)) {
  const ctx = await browser.newContext(); const p = await ctx.newPage();
  await p.goto(`${WEB}/register`);
  await p.locator('input[autocomplete="name"]').fill(u.name);
  await p.fill('input[type="email"]', u.email);
  await p.fill('input[type="password"]', PASS);
  await p.locator('input[autocomplete="tel"]').fill(u.phone);
  await p.locator("form label.field:has-text('') input.input").last().fill(u.city);
  await p.click("button.btn.primary");
  await p.waitForURL(`${WEB}/`).catch(async () => console.log("  register", who, await p.locator(".alert").textContent().catch(() => "?")));
  console.log("registered", u.name);
  await ctx.close();
}

// 2. each family / finder posts their report from the form
const urls = [];
for (const r of REPORTS) {
  const url = await as(r.who, r.geo, async (p) => {
    await p.goto(`${WEB}/reports/new`);
    await p.locator(".segmented button").nth(r.kind === "missing" ? 0 : 1).click();
    const text = p.locator("form .fields input.input:not([type])");
    if (r.child) await text.nth(0).fill(r.child);
    await p.locator("form select.input").first().selectOption(r.gender);
    await p.locator('form input[type="number"]').fill(String(r.age));
    await p.locator('form input[type="date"]').fill(r.date);
    await text.nth(1).fill(r.city);
    await text.nth(2).fill(r.area);
    await p.click("text=📍");
    await p.waitForTimeout(300);
    await p.locator("form textarea").fill(r.desc);
    for (const [i, f] of r.photos.entries()) {
      await p.setInputFiles('input[type="file"]', ph(f));
      await p.waitForFunction((n) => !document.querySelector(".progress") && document.querySelectorAll(".tile img").length === n, i + 1);
    }
    await p.click("form button.btn.primary");
    await p.waitForURL(/\/reports\/[0-9a-f-]{36}$/);
    return p.url();
  });
  urls.push(url);
  console.log("posted", r.kind, r.child || "(no name)", url);
}

// 3. the community: comments and solidarity likes
for (const c of COMMENTS) {
  await as(c.who, null, async (p) => {
    await p.goto(urls[c.on]);
    const box = p.locator("input.input.grow");
    await box.fill(c.text);
    await box.press("Enter");
    await p.locator(".comment", { hasText: c.text.slice(0, 20) }).waitFor();
  });
}
for (const [i, who] of Object.entries(LIKES)) for (const w of who) {
  await as(w, null, async (p) => { await p.goto(urls[i]); await p.locator("button:has-text('♥')").click(); await p.waitForTimeout(400); });
}
console.log("comments", COMMENTS.length, "likes", Object.values(LIKES).flat().length);
fs.writeFileSync(path.join(HERE, "clips/report-urls.json"), JSON.stringify(urls, null, 1));
await browser.close();
