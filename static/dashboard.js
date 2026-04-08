/* ── EcomInsight Dashboard JS ─────────────────────────────────── */
"use strict";

const API = "";          // same-origin; change if backend runs elsewhere
const ACCENT   = "#4a90d9";
const ACCENT2  = "#f0c040";
const GREEN    = "#3dd68c";
const SURFACE2 = "#172034";
const TEXT_MUT = "#8494ad";
const PALETTE  = ["#4a90d9","#f0c040","#3dd68c","#e87040","#a06ed9","#e86090","#40c0d9","#90d940"];

Chart.defaults.color        = TEXT_MUT;
Chart.defaults.borderColor  = "#1e2d47";
Chart.defaults.font.family  = "'DM Sans', sans-serif";
Chart.defaults.font.size    = 12;

// ── State ──────────────────────────────────────────────────────────
let charts = {};

// ── Helpers ───────────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const fmt$ = n  => "$" + Number(n).toLocaleString("en-US", {minimumFractionDigits: 2, maximumFractionDigits: 2});
const fmtN = n  => Number(n).toLocaleString("en-US");

function buildURL(endpoint, extra = {}) {
  const start = $("start-date").value;
  const end   = $("end-date").value;
  const params = new URLSearchParams();
  if (start) params.set("start_date", start);
  if (end)   params.set("end_date",   end);
  Object.entries(extra).forEach(([k,v]) => params.set(k, v));
  const qs = params.toString();
  return `${API}${endpoint}${qs ? "?" + qs : ""}`;
}

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API error ${res.status}: ${url}`);
  return res.json();
}

function destroyChart(id) {
  if (charts[id]) { charts[id].destroy(); delete charts[id]; }
}

// ── KPIs ──────────────────────────────────────────────────────────
async function loadKPIs() {
  const data = await fetchJSON(buildURL("/api/kpis"));
  $("val-revenue").textContent   = fmt$(data.total_revenue);
  $("val-orders").textContent    = fmtN(data.total_orders);
  $("val-aov").textContent       = fmt$(data.avg_order_value);
  $("val-customers").textContent = fmtN(data.unique_customers);
  $("val-units").textContent     = fmtN(data.total_units_sold);
}

// ── Monthly Revenue Chart ─────────────────────────────────────────
async function loadMonthlyChart() {
  const data = await fetchJSON(buildURL("/api/sales_by_month"));
  const labels = data.map(d => d.month);
  const values = data.map(d => d.revenue);

  destroyChart("monthly");
  charts["monthly"] = new Chart($("chart-monthly"), {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Revenue",
        data: values,
        borderColor: ACCENT,
        backgroundColor: "rgba(74,144,217,.12)",
        pointBackgroundColor: ACCENT,
        pointRadius: 4,
        pointHoverRadius: 6,
        borderWidth: 2,
        tension: 0.4,
        fill: true,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { display: false },
                 tooltip: { callbacks: { label: ctx => " " + fmt$(ctx.raw) } } },
      scales: {
        x: { ticks: { maxTicksLimit: 12, maxRotation: 45 } },
        y: { ticks: { callback: v => "$" + (v >= 1000 ? (v/1000).toFixed(0)+"k" : v) } }
      }
    }
  });
}

// ── Category Doughnut ─────────────────────────────────────────────
async function loadCategoryChart(canvasId = "chart-category") {
  const data = await fetchJSON(buildURL("/api/sales_by_category"));
  const labels = data.map(d => d.category);
  const values = data.map(d => d.revenue);

  destroyChart(canvasId);
  charts[canvasId] = new Chart($(canvasId), {
    type: "doughnut",
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: PALETTE, borderWidth: 0, hoverOffset: 8 }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      cutout: "62%",
      plugins: {
        legend: { position: "right", labels: { boxWidth: 12, padding: 12 } },
        tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${fmt$(ctx.raw)}` } }
      }
    }
  });
}

// ── Quarterly Bar Chart ───────────────────────────────────────────
async function loadQuarterlyChart() {
  const data = await fetchJSON("/api/orders_by_quarter");
  const labels  = data.map(d => d.label);
  const revenue = data.map(d => d.revenue);
  const orders  = data.map(d => d.orders);

  destroyChart("quarterly");
  charts["quarterly"] = new Chart($("chart-quarterly"), {
    type: "bar",
    data: {
      labels,
      datasets: [
        { label: "Revenue ($)", data: revenue, backgroundColor: ACCENT,  yAxisID: "y", borderRadius: 6 },
        { label: "Orders",      data: orders,  backgroundColor: ACCENT2, yAxisID: "y2", borderRadius: 6 },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { position: "top" } },
      scales: {
        y:  { position: "left",  ticks: { callback: v => "$" + (v/1000).toFixed(0)+"k" } },
        y2: { position: "right", grid: { drawOnChartArea: false } }
      }
    }
  });
}

// ── Top Products Horizontal Bar ───────────────────────────────────
async function loadTopProductsChart() {
  const data = await fetchJSON(buildURL("/api/top_products", { n: 10 }));
  const labels = data.map(d => d.product_name);
  const values = data.map(d => d.total_revenue);

  destroyChart("top_products");
  charts["top_products"] = new Chart($("chart-top-products"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Revenue",
        data: values,
        backgroundColor: PALETTE,
        borderRadius: 6,
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { display: false },
                 tooltip: { callbacks: { label: ctx => " " + fmt$(ctx.raw) } } },
      scales: {
        x: { ticks: { callback: v => "$" + (v/1000).toFixed(0)+"k" } }
      }
    }
  });
}

// ── Customer Stats ────────────────────────────────────────────────
async function loadCustomerView() {
  const [stats, catData] = await Promise.all([
    fetchJSON("/api/customer_stats"),
    fetchJSON(buildURL("/api/sales_by_category"))
  ]);

  $("cust-avg-spend").textContent = fmt$(stats.avg_spend_per_customer);
  $("cust-max-spend").textContent = fmt$(stats.max_spend);
  $("cust-repeat").textContent    = fmtN(stats.repeat_customers);
  $("cust-onetime").textContent   = fmtN(stats.one_time_customers);

  // Re-use category chart in customers view
  const labels = catData.map(d => d.category);
  const values = catData.map(d => d.revenue);
  destroyChart("cust-cat");
  charts["cust-cat"] = new Chart($("chart-cust-cat"), {
    type: "bar",
    data: {
      labels,
      datasets: [{ label: "Revenue", data: values, backgroundColor: PALETTE, borderRadius: 6 }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { display: false },
                 tooltip: { callbacks: { label: ctx => " " + fmt$(ctx.raw) } } },
      scales: { y: { ticks: { callback: v => "$" + (v/1000).toFixed(0)+"k" } } }
    }
  });

  // Repeat vs One-time pie
  destroyChart("cust-type");
  charts["cust-type"] = new Chart($("chart-cust-type"), {
    type: "pie",
    data: {
      labels: ["Repeat Customers", "One-Time Buyers"],
      datasets: [{ data: [stats.repeat_customers, stats.one_time_customers],
                   backgroundColor: [ACCENT, ACCENT2], borderWidth: 0, hoverOffset: 8 }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { position: "bottom" } }
    }
  });
}

// ── Products Table ────────────────────────────────────────────────
async function loadProductsTable() {
  const data = await fetchJSON(buildURL("/api/top_products", { n: 50 }));
  const tbody = $("products-tbody");
  tbody.innerHTML = data.map((p, i) => `
    <tr>
      <td>${i+1}</td>
      <td>${p.product_name}</td>
      <td><span style="background:rgba(74,144,217,.15);color:#4a90d9;padding:.2rem .55rem;border-radius:20px;font-size:.78rem">${p.product_category}</span></td>
      <td>${fmt$(p.total_revenue)}</td>
      <td>${fmtN(p.total_orders)}</td>
      <td>${fmt$(p.total_revenue / p.total_orders)}</td>
    </tr>
  `).join("");
}

// ── Navigation ────────────────────────────────────────────────────
const VIEWS = {
  dashboard: {
    title: "Overview",
    load: () => Promise.all([loadKPIs(), loadMonthlyChart(), loadCategoryChart(), loadQuarterlyChart(), loadTopProductsChart()])
  },
  products: {
    title: "Product Performance",
    load: loadProductsTable
  },
  customers: {
    title: "Customer Insights",
    load: loadCustomerView
  },
  reports: {
    title: "Reports",
    load: () => {}
  }
};

let currentView = "dashboard";

function switchView(name) {
  if (!VIEWS[name]) return;
  currentView = name;

  document.querySelectorAll(".view").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".nav-link").forEach(el => el.classList.remove("active"));

  document.getElementById(`view-${name}`).classList.add("active");
  document.querySelector(`[data-view="${name}"]`).classList.add("active");
  $("page-title").textContent = VIEWS[name].title;

  VIEWS[name].load().catch(err => console.error("Load error:", err));
}

// ── Report download ───────────────────────────────────────────────
$("btn-download").addEventListener("click", () => {
  const start  = $("rpt-start").value;
  const end    = $("rpt-end").value;
  const format = $("rpt-format").value;
  const params = new URLSearchParams({ format });
  if (start) params.set("start_date", start);
  if (end)   params.set("end_date",   end);
  const url = `${API}/api/generate_report?${params}`;
  $("rpt-status").textContent = "Generating…";
  // Trigger download by creating a hidden link
  const a = document.createElement("a");
  a.href = url;
  a.style.display = "none";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => { $("rpt-status").textContent = "✓ Download started!"; }, 500);
  setTimeout(() => { $("rpt-status").textContent = ""; }, 4000);
});

// ── Filter buttons ────────────────────────────────────────────────
$("btn-apply").addEventListener("click", () => VIEWS[currentView].load().catch(console.error));
$("btn-reset").addEventListener("click", () => {
  $("start-date").value = "";
  $("end-date").value   = "";
  VIEWS[currentView].load().catch(console.error);
});

// ── Nav links ─────────────────────────────────────────────────────
document.querySelectorAll(".nav-link").forEach(link => {
  link.addEventListener("click", e => {
    e.preventDefault();
    switchView(link.dataset.view);
  });
});

// ── Boot ──────────────────────────────────────────────────────────
switchView("dashboard");
