// ==========================================================================
// QA Control Center Dashboard Logic & Backend Integration
// ==========================================================================

let findingsData = [];
let automationTestsData = [];
let pollingInterval = null;

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initEventListeners();
  loadDashboardData();
  pollTestStatus();
});

// Tab Switching
function initTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const target = tab.getAttribute("data-target");
      switchTab(target);
    });
  });

  const galleryTabs = document.querySelectorAll(".gallery-tab");
  galleryTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      galleryTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      filterGallery(tab.getAttribute("data-filter"));
    });
  });
}

function switchTab(tabId) {
  document.querySelectorAll(".nav-tab").forEach(t => {
    t.classList.toggle("active", t.getAttribute("data-target") === tabId);
  });
  document.querySelectorAll(".tab-panel").forEach(p => {
    p.classList.toggle("active", p.id === tabId);
  });
}

// Event Listeners
function initEventListeners() {
  document.getElementById("btnRefreshStats")?.addEventListener("click", () => {
    loadDashboardData();
    showToast("Dashboard stats refreshed", "success");
  });

  document.getElementById("btnRunFullSuite")?.addEventListener("click", () => {
    runTestSuite();
  });

  document.getElementById("btnClearConsole")?.addEventListener("click", () => {
    document.getElementById("consoleOutput").textContent = "Console cleared. Ready for next test run.";
  });

  document.getElementById("btnGenerateExcel")?.addEventListener("click", generateExcel);
  document.getElementById("btnRebuildExcel")?.addEventListener("click", generateExcel);

  // Filters for findings
  document.getElementById("findingsSearch")?.addEventListener("input", filterFindings);
  document.getElementById("severityFilter")?.addEventListener("change", filterFindings);
  document.getElementById("typeFilter")?.addEventListener("change", filterFindings);

  // Modal Lightbox
  const modal = document.getElementById("imageModal");
  const modalClose = document.getElementById("modalClose");
  const modalBackdrop = document.getElementById("modalBackdrop");

  modalClose?.addEventListener("click", () => modal.classList.remove("active"));
  modalBackdrop?.addEventListener("click", () => modal.classList.remove("active"));
}

// Load Initial Data
async function loadDashboardData() {
  try {
    const [statsRes, findingsRes, testsRes] = await Promise.all([
      fetch("/api/stats").then(r => r.json()),
      fetch("/api/findings").then(r => r.json()),
      fetch("/api/automation-tests").then(r => r.json())
    ]);

    findingsData = findingsRes;
    automationTestsData = testsRes;

    updateStatsUI(statsRes);
    renderFindings(findingsData);
    renderTestCatalog(automationTestsData);
    renderGallery();
  } catch (err) {
    console.error("Failed to load dashboard data:", err);
    showToast("Error connecting to QA backend API", "error");
  }
}

// Update Top Metric Stat Cards
function updateStatsUI(stats) {
  if (!stats) return;
  document.getElementById("statPassRate").textContent = stats.automation.pass_rate || "100%";
  document.getElementById("statTotalTests").textContent = stats.automation.total || "16";
  document.getElementById("statFindingsCount").textContent = stats.product_findings.total || "10";
  document.getElementById("statDuration").textContent = stats.automation.last_duration || "~97s";
}

// Render Findings Matrix
function renderFindings(items) {
  const container = document.getElementById("findingsContainer");
  if (!container) return;

  if (items.length === 0) {
    container.innerHTML = `<div class="text-muted" style="grid-column: 1/-1; padding: 40px; text-align: center;">No findings match the selected filters.</div>`;
    return;
  }

  container.innerHTML = items.map(item => {
    let sevBadge = item.severity === "High" ? "badge-danger" : item.severity === "Medium" ? "badge-warning" : "badge-info";
    let typeTag = item.type.includes("Bug") ? "tag-functional" : item.type.includes("UX") ? "tag-ux" : "tag-positive";

    return `
      <div class="finding-card">
        <div class="finding-top">
          <span class="finding-id">${item.id}</span>
          <div style="display:flex; gap:6px;">
            <span class="tag ${typeTag}">${item.type}</span>
            <span class="badge ${sevBadge}">${item.severity}</span>
          </div>
        </div>
        <h4 class="finding-title">${item.title}</h4>
        
        <div class="finding-detail-box">
          <div class="detail-row">
            <strong>Module / Flow:</strong> ${item.module} &rsaquo; ${item.feature}
          </div>
          <div class="detail-row">
            <strong>Expected:</strong> ${item.expected}
          </div>
          <div class="detail-row">
            <strong>Actual:</strong> ${item.actual}
          </div>
        </div>

        <div class="finding-thumb-container">
          <img src="/evidence/${item.image}" alt="${item.id} primary evidence" class="finding-thumb" onclick="openModal('/evidence/${item.image}', '${item.id}: ${item.title}', 'Primary Evidence Screenshot')">
          ${item.secondary_image ? `
            <img src="/evidence/${item.secondary_image}" alt="${item.id} secondary evidence" class="finding-thumb" onclick="openModal('/evidence/${item.secondary_image}', '${item.id}: ${item.title}', 'Secondary State Screenshot')">
          ` : ""}
        </div>
      </div>
    `;
  }).join("");
}

function filterFindings() {
  const q = (document.getElementById("findingsSearch")?.value || "").toLowerCase();
  const sev = document.getElementById("severityFilter")?.value || "ALL";
  const typ = document.getElementById("typeFilter")?.value || "ALL";

  const filtered = findingsData.filter(item => {
    const matchQ = item.title.toLowerCase().includes(q) || item.module.toLowerCase().includes(q) || item.id.toLowerCase().includes(q);
    const matchSev = sev === "ALL" || item.severity === sev;
    const matchTyp = typ === "ALL" || item.type.toLowerCase().includes(typ.toLowerCase());
    return matchQ && matchSev && matchTyp;
  });

  renderFindings(filtered);
}

// Render Automation Scenarios Catalog
function renderTestCatalog(tests) {
  const container = document.getElementById("testsCatalogGrid");
  if (!container) return;

  container.innerHTML = tests.map(t => {
    const isPositive = t.type === "Positive";
    const typeBadge = isPositive ? "badge-success" : "badge-warning";
    const tagClass = t.module === "Auth" ? "tag-auth" : t.module === "Catalog" ? "tag-catalog" : t.module === "Cart" ? "tag-cart" : "tag-security";

    return `
      <div class="test-card">
        <div>
          <div class="test-header">
            <span class="tag ${tagClass}">${t.module}</span>
            <span class="badge ${typeBadge}">${t.type}</span>
          </div>
          <div class="test-title">${t.class}::${t.method}</div>
          <div class="test-desc">${t.desc}</div>
        </div>
        <div class="test-footer">
          <button class="btn btn-outline btn-sm" onclick="runIsolatedTest('${t.method}')">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            Run Isolated
          </button>
          <button class="btn-icon" onclick="openModal('/evidence/${t.image}', '${t.method}', '${t.desc}')" title="View Evidence">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          </button>
        </div>
      </div>
    `;
  }).join("");
}

// Render Evidence Gallery
function renderGallery() {
  const container = document.getElementById("galleryGrid");
  if (!container) return;

  const images = [
    { src: "saucedemo/tc01_valid_login_success.png", title: "Valid Login Dashboard", cat: "saucedemo", sub: "TC01: Product Catalog Landing" },
    { src: "saucedemo/tc02_locked_out_user.png", title: "Locked Out User Error", cat: "saucedemo", sub: "TC02: Guard Rejection Banner" },
    { src: "saucedemo/tc03c_sort_price_low_high.png", title: "Price Sort Verification", cat: "saucedemo", sub: "TC03: Low-to-High Price Order" },
    { src: "saucedemo/tc04_add_single_item.png", title: "Single Item Cart Add", cat: "saucedemo", sub: "TC04: Badge '1' & Button Toggle" },
    { src: "saucedemo/tc04_add_two_items.png", title: "Multi Item Cart Add", cat: "saucedemo", sub: "TC04: Badge '2' Increment" },
    { src: "saucedemo/tc05_cart_content.png", title: "Cart Items Rendered", cat: "saucedemo", sub: "TC05: Shopping Cart Contents" },
    { src: "saucedemo/tc05b_remove_from_cart.png", title: "Cart Item Removal", cat: "saucedemo", sub: "TC05: Badge Reset on Delete" },
    { src: "saucedemo/tc06_checkout_complete.png", title: "Checkout Completed Order", cat: "saucedemo", sub: "TC06: Order Confirmation & Badge Clear" },
    { src: "saucedemo/tc07_logout.png", title: "Session Logout Redirection", cat: "saucedemo", sub: "TC07: Return to Login Screen" },
    { src: "recruitment_phone_letters.png", title: "Recruitment Phone String Bug", cat: "orangehrm", sub: "PL-01: Alphabetical Input Persisted" },
    { src: "pim_after_reset.png", title: "PIM Filter Reset UX Issue", cat: "orangehrm", sub: "PL-02: Stale Filtered Dataset" },
    { src: "auth_back_navigation.png", title: "Post-Logout Cached Back Nav", cat: "orangehrm", sub: "PL-03: Cached Dashboard Metrics" },
    { src: "leave_date_validation_verified.png", title: "Date Inversion Guard", cat: "orangehrm", sub: "PL-06: Inline Negative Date Error" },
    { src: "admin_duplicate_username.png", title: "Username Duplicate Check", cat: "orangehrm", sub: "PL-07: Real-time Debounced Validation" },
    { src: "pim_bulk_selection.png", title: "Bulk Record Selection", cat: "orangehrm", sub: "PL-09: Batch Select 50 Cards" }
  ];

  container.innerHTML = images.map(img => `
    <div class="gallery-item" data-cat="${img.cat}" onclick="openModal('/evidence/${img.src}', '${img.title}', '${img.sub}')">
      <img src="/evidence/${img.src}" alt="${img.title}" class="gallery-img">
      <div class="gallery-info">
        <div class="gallery-title">${img.title}</div>
        <div class="gallery-sub">${img.sub}</div>
      </div>
    </div>
  `).join("");
}

function filterGallery(category) {
  document.querySelectorAll(".gallery-item").forEach(el => {
    if (category === "all" || el.getAttribute("data-cat") === category) {
      el.style.display = "block";
    } else {
      el.style.display = "none";
    }
  });
}

// Test Runner Triggers
async function runTestSuite() {
  switchTab("tab-runner");
  const consoleEl = document.getElementById("consoleOutput");
  consoleEl.textContent = "Initiating test run request to backend...\n";

  try {
    const res = await fetch("/api/run-tests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    const data = await res.json();
    if (res.ok) {
      showToast("Test suite execution started!", "success");
      pollTestStatus();
    } else {
      showToast(data.message || "Failed to start tests", "error");
    }
  } catch (err) {
    showToast("API communication failure", "error");
  }
}

async function runIsolatedTest(testMethod) {
  switchTab("tab-runner");
  const consoleEl = document.getElementById("consoleOutput");
  consoleEl.textContent = `Initiating isolated test: ${testMethod}...\n`;

  try {
    const res = await fetch("/api/run-tests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filter: testMethod })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(`Running ${testMethod}...`, "success");
      pollTestStatus();
    } else {
      showToast(data.message || "Failed to start isolated test", "error");
    }
  } catch (err) {
    showToast("API communication failure", "error");
  }
}

function pollTestStatus() {
  if (pollingInterval) clearInterval(pollingInterval);

  pollingInterval = setInterval(async () => {
    try {
      const res = await fetch("/api/test-status");
      const state = await res.json();

      const pill = document.getElementById("liveStatusPill");
      const pillText = document.getElementById("statusPillText");
      const consoleEl = document.getElementById("consoleOutput");

      if (consoleEl) {
        consoleEl.textContent = state.logs || "Ready.";
        consoleEl.scrollTop = consoleEl.scrollHeight;
      }

      if (state.is_running) {
        pill.classList.add("running");
        pillText.textContent = "Running Tests...";
      } else {
        pill.classList.remove("running");
        pillText.textContent = state.status === "COMPLETED" ? "All Tests Passed" : (state.status === "FAILED" ? "Tests Failed" : "Runner Ready");
        if (state.status === "COMPLETED" || state.status === "FAILED") {
          loadDashboardData(); // Refresh metrics
        }
      }
    } catch (err) {
      console.error("Error polling test status:", err);
    }
  }, 1200);
}

// Excel Report Generation
async function generateExcel() {
  showToast("Compiling QA_Assessment_Report.xlsx...", "info");
  try {
    const res = await fetch("/api/generate-excel", { method: "POST" });
    const data = await res.json();
    if (res.ok) {
      showToast("QA_Assessment_Report.xlsx successfully generated!", "success");
    } else {
      showToast(data.error || "Excel generation failed", "error");
    }
  } catch (err) {
    showToast("Error generating report", "error");
  }
}

// Modal Lightbox
function openModal(src, title, caption) {
  const modal = document.getElementById("imageModal");
  document.getElementById("modalImage").src = src;
  document.getElementById("modalTitle").textContent = title;
  document.getElementById("modalCaption").textContent = caption;
  modal.classList.add("active");
}

// Toast System
function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
