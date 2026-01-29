const translations = {
  en: {
    "dashboard.subtitle": "Governance Compliance",
    "dashboard.title": "Governance Compliance Dashboard",
    "dashboard.date": "Date",
    "kpi.compliance": "Compliance Rate",
    "kpi.compliance_hint": "All checks pass across active repos.",
    "kpi.drift_rate": "Drift Rate",
    "kpi.drift_hint": "Index consistency drift.",
    "kpi.bundle_compliance": "Evidence Bundle Compliance",
    "kpi.bundle_hint": "5-core files integrity coverage.",
    "kpi.repo_health": "Repo Health",
    "kpi.health_hint": "Average check pass ratio.",
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
    "panel.boundary": "Trust Boundary Map",
    "panel.boundary_hint": "Repo grouping by control/execution/asset layers.",
    "boundary.control": "Control Plane",
    "boundary.execution": "Execution Plane",
    "boundary.asset": "Asset Layer",
    "boundary.docs": "Documentation",
    "table.repo": "Repo",
    "table.type": "Boundary",
    "table.compliance": "Compliance",
    "table.failing": "Failing Checks",
    "data.source": "Data Source",
    "axis.time": "Time",
    "axis.rate": "Rate (%)",
    "axis.health": "Health (%)",
    "trend.title": "Compliance Trend",
    "trend.subtitle": "Rolling view of nightly compliance.",
    "trend.legend": "Compliance Rate",
    "trend.drift_title": "Drift Trend",
    "trend.drift_subtitle": "Index drift rate over time.",
    "trend.drift_legend": "Drift Rate",
    "trend.health_title": "Repo Health Trend",
    "trend.health_subtitle": "Average check pass ratio.",
    "trend.health_legend": "Repo Health",
    "trend.empty": "Collecting data…",
    "trend.latest": "Latest",
    "trend.delta": "Change",
    "trend.threshold": "Threshold",
  },
  zh: {
    "dashboard.subtitle": "治理合規",
    "dashboard.title": "治理合規儀表板",
    "dashboard.date": "日期",
    "kpi.compliance": "合規率",
    "kpi.compliance_hint": "所有活動 Repo 的檢查結果。",
    "kpi.drift_rate": "漂移率",
    "kpi.drift_hint": "索引一致性漂移。",
    "kpi.bundle_compliance": "證據包完整率",
    "kpi.bundle_hint": "5 核心檔完整性覆蓋。",
    "kpi.repo_health": "Repo 健康度",
    "kpi.health_hint": "平均檢查通過比例。",
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
    "panel.boundary": "信任邊界分層",
    "panel.boundary_hint": "依控制面 / 執行面 / 資產層分組。",
    "boundary.control": "控制面",
    "boundary.execution": "執行面",
    "boundary.asset": "資產層",
    "boundary.docs": "文件層",
    "table.repo": "Repo",
    "table.type": "邊界",
    "table.compliance": "合規",
    "table.failing": "未通過檢查",
    "data.source": "資料來源",
    "axis.time": "時間",
    "axis.rate": "比例 (%)",
    "axis.health": "健康度 (%)",
    "trend.title": "合規趨勢",
    "trend.subtitle": "每晚稽核的合規走勢。",
    "trend.legend": "合規率",
    "trend.drift_title": "漂移趨勢",
    "trend.drift_subtitle": "索引漂移率時間序列。",
    "trend.drift_legend": "漂移率",
    "trend.health_title": "Repo 健康趨勢",
    "trend.health_subtitle": "平均檢查通過比例。",
    "trend.health_legend": "Repo 健康度",
    "trend.empty": "資料累積中…",
    "trend.latest": "最新",
    "trend.delta": "變動",
    "trend.threshold": "門檻",
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

function formatRate(value) {
  if (value === null || value === undefined) {
    return "--";
  }
  const pct = (value * 100).toFixed(1) + "%";
  return pct;
}

function renderTrendSeries(entries, metricKey, dom) {
  const emptyEl = document.getElementById(dom.empty);
  const line = document.getElementById(dom.line);
  const area = document.getElementById(dom.area);
  const chart = document.getElementById(dom.chart);
  const latestEl = document.querySelector(`[data-metric="${dom.latest}"]`);
  const deltaEl = document.querySelector(`[data-metric="${dom.delta}"]`);
  const width = 600;
  const height = 180;
  const padding = 16;

  if (!entries || entries.length < 2) {
    if (emptyEl) emptyEl.style.display = "flex";
    if (line) line.setAttribute("d", "");
    if (area) area.setAttribute("d", "");
    if (latestEl) latestEl.textContent = "--";
    if (deltaEl) deltaEl.textContent = "--";
    if (chart) {
      const fallback = [
        { date: "-" },
        { date: "-" },
        { date: "-" },
      ];
      renderAxisTicks(chart, fallback, 2, width, height, padding);
    }
    return;
  }

  const points = entries.map((item, idx) => ({
    x: idx,
    y: item[metricKey],
  }));
  const maxX = points.length - 1;

  const toX = (x) => padding + (x / maxX) * (width - padding * 2);
  const toY = (y) => padding + (1 - y) * (height - padding * 2);

  const path = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${toX(p.x)} ${toY(p.y)}`)
    .join(" ");

  const areaPath = `${path} L ${toX(maxX)} ${height - padding} L ${toX(0)} ${height - padding} Z`;

  line.setAttribute("d", path);
  area.setAttribute("d", areaPath);
  if (emptyEl) emptyEl.style.display = "none";

  if (chart) {
    renderAxisTicks(chart, entries, maxX, width, height, padding);
  }

  const latest = entries[entries.length - 1][metricKey];
  const prev = entries[entries.length - 2][metricKey];
  const delta = latest - prev;
  latestEl.textContent = formatRate(latest);
  const sign = delta > 0 ? "+" : "";
  deltaEl.textContent = `${sign}${(delta * 100).toFixed(1)}%`;
  deltaEl.style.color = delta >= 0 ? "var(--success)" : "var(--danger)";
}

function renderAxisTicks(chart, entries, maxX, width, height, padding) {
  clearAxisTicks(chart);
  const xTicks = [0, Math.floor(maxX / 2), maxX];
  const yTicks = [0, 0.5, 1];

  xTicks.forEach((idx) => {
    if (idx < 0 || idx > maxX) return;
    const entry = entries[idx] || {};
    const label = entry.date ? String(entry.date) : String(idx + 1);
    const x = padding + (idx / maxX) * (width - padding * 2);
    const y = height - 2;
    chart.appendChild(makeSvgText(x, y, label, "end"));
  });

  yTicks.forEach((val) => {
    const x = padding;
    const y = padding + (1 - val) * (height - padding * 2) + 3;
    chart.appendChild(makeSvgText(x, y, formatRate(val), "start"));
  });
}

function clearAxisTicks(chart) {
  chart.querySelectorAll(".axis-tick").forEach((node) => node.remove());
}

function makeSvgText(x, y, text, anchor) {
  const el = document.createElementNS("http://www.w3.org/2000/svg", "text");
  el.setAttribute("x", String(x));
  el.setAttribute("y", String(y));
  el.setAttribute("text-anchor", anchor);
  el.setAttribute("class", "axis-tick");
  el.textContent = text;
  return el;
}

async function loadMetrics() {
  try {
    const res = await fetch("metrics.json", { cache: "no-store" });
    if (!res.ok) {
      throw new Error("metrics fetch failed");
    }
    const data = await res.json();
    renderTrendSeries(data, "compliance_rate", {
      empty: "trend-empty",
      line: "trend-line",
      area: "trend-area",
      chart: "trend-chart",
      latest: "latest-rate",
      delta: "delta-rate",
    });
    renderTrendSeries(data, "drift_rate", {
      empty: "drift-empty",
      line: "drift-line",
      area: "drift-area",
      chart: "drift-chart",
      latest: "latest-drift",
      delta: "delta-drift",
    });
    renderTrendSeries(data, "repo_health", {
      empty: "health-empty",
      line: "health-line",
      area: "health-area",
      chart: "health-chart",
      latest: "latest-health",
      delta: "delta-health",
    });
  } catch (err) {
    try {
      const res = await fetch("trends.json", { cache: "no-store" });
      if (!res.ok) {
        throw new Error("trends fetch failed");
      }
      const data = await res.json();
      renderTrendSeries(data, "compliance_rate", {
        empty: "trend-empty",
        line: "trend-line",
        area: "trend-area",
        chart: "trend-chart",
        latest: "latest-rate",
        delta: "delta-rate",
      });
    } catch (err2) {
      renderTrendSeries([], "compliance_rate", {
        empty: "trend-empty",
        line: "trend-line",
        area: "trend-area",
        chart: "trend-chart",
        latest: "latest-rate",
        delta: "delta-rate",
      });
    }
    renderTrendSeries([], "drift_rate", {
      empty: "drift-empty",
      line: "drift-line",
      area: "drift-area",
      chart: "drift-chart",
      latest: "latest-drift",
      delta: "delta-drift",
    });
    renderTrendSeries([], "repo_health", {
      empty: "health-empty",
      line: "health-line",
      area: "health-area",
      chart: "health-chart",
      latest: "latest-health",
      delta: "delta-health",
    });
  }
}

async function loadTrend(lang) {
  try {
    const res = await fetch("trends.json", { cache: "no-store" });
    if (!res.ok) {
      renderTrendSeries([], "compliance_rate", {
        empty: "trend-empty",
        line: "trend-line",
        area: "trend-area",
        chart: "trend-chart",
        latest: "latest-rate",
        delta: "delta-rate",
      });
      return;
    }
    const data = await res.json();
    renderTrendSeries(data, "compliance_rate", {
      empty: "trend-empty",
      line: "trend-line",
      area: "trend-area",
      chart: "trend-chart",
      latest: "latest-rate",
      delta: "delta-rate",
    });
  } catch (err) {
    renderTrendSeries([], "compliance_rate", {
      empty: "trend-empty",
      line: "trend-line",
      area: "trend-area",
      chart: "trend-chart",
      latest: "latest-rate",
      delta: "delta-rate",
    });
  }
}

const savedTheme = localStorage.getItem("aaa-dashboard-theme") || "light";
const savedLang = localStorage.getItem("aaa-dashboard-lang") || "en";
setTheme(savedTheme);
setLang(savedLang);
loadMetrics();

themeToggle.addEventListener("click", () => {
  setTheme(root.dataset.theme === "dark" ? "light" : "dark");
});

langToggle.addEventListener("click", () => {
  const nextLang = root.dataset.lang === "en" ? "zh" : "en";
  setLang(nextLang);
  loadMetrics();
});
