const translations = {
  en: {
    "dashboard.subtitle": "Governance Compliance",
    "dashboard.title": "Governance Compliance Dashboard",
    "dashboard.date": "Date",
    "kpi.compliance": "Compliance Rate",
    "kpi.compliance_hint": "All checks pass across active repos.",
    "kpi.total_repos": "Total Repos",
    "kpi.active_repos": "Active",
    "kpi.failing_repos": "Failing Repos",
    "kpi.failing_hint": "Requires action.",
    "kpi.archived_repos": "Archived",
    "kpi.archived_hint": "Excluded from rate.",
    "panel.failing": "Failing Repos",
    "panel.failing_hint": "Highest priority remediation list.",
    "panel.failing_empty": "All repos compliant",
    "panel.inventory": "Repo Inventory",
    "panel.inventory_hint": "Full list with compliance status.",
    "table.repo": "Repo",
    "table.type": "Type",
    "table.compliance": "Compliance",
    "table.failing": "Failing Checks",
  },
  zh: {
    "dashboard.subtitle": "治理合規",
    "dashboard.title": "治理合規儀表板",
    "dashboard.date": "日期",
    "kpi.compliance": "合規率",
    "kpi.compliance_hint": "所有活動 Repo 的檢查結果。",
    "kpi.total_repos": "Repo 總數",
    "kpi.active_repos": "參與計算",
    "kpi.failing_repos": "不合規",
    "kpi.failing_hint": "需優先處理。",
    "kpi.archived_repos": "已封存",
    "kpi.archived_hint": "不納入合規率。",
    "panel.failing": "不合規清單",
    "panel.failing_hint": "最高優先處理列表。",
    "panel.failing_empty": "全部合規",
    "panel.inventory": "Repo 清單",
    "panel.inventory_hint": "全量與合規狀態。",
    "table.repo": "Repo",
    "table.type": "類型",
    "table.compliance": "合規",
    "table.failing": "未通過檢查",
  },
};

const statusLabels = {
  en: { pass: "PASS", fail: "FAIL", archived: "ARCHIVED" },
  zh: { pass: "合格", fail: "未通過", archived: "封存" },
};

const root = document.documentElement;
const themeToggle = document.getElementById("theme-toggle");
const langToggle = document.getElementById("lang-toggle");

function setTheme(theme) {
  root.dataset.theme = theme;
  themeToggle.textContent = theme === "dark" ? "Light" : "Dark";
  localStorage.setItem("aaa-dashboard-theme", theme);
}

function setLang(lang) {
  root.dataset.lang = lang;
  const dict = translations[lang] || translations.en;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.textContent = dict[key];
    }
  });
  document.querySelectorAll("[data-status]").forEach((el) => {
    const key = el.getAttribute("data-status");
    el.textContent = (statusLabels[lang] || statusLabels.en)[key] || key;
  });
  langToggle.textContent = lang === "en" ? "中文" : "EN";
  localStorage.setItem("aaa-dashboard-lang", lang);
}

const savedTheme = localStorage.getItem("aaa-dashboard-theme") || "light";
const savedLang = localStorage.getItem("aaa-dashboard-lang") || "en";
setTheme(savedTheme);
setLang(savedLang);

themeToggle.addEventListener("click", () => {
  setTheme(root.dataset.theme === "dark" ? "light" : "dark");
});

langToggle.addEventListener("click", () => {
  setLang(root.dataset.lang === "en" ? "zh" : "en");
});
