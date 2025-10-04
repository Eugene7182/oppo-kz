/**
 * Responsive dashboard prototype for OPPO KZ.
 * Pure JS implementation with in-memory demo data.
 */
const state = {
  currentRole: "admin",
  chart: {
    grain: "day",
    secondaryAxis: false,
  },
  filters: {
    office: {
      scope: ["Все"],
      period: ["Текущий месяц"],
      timeGrain: ["День"],
      models: ["Reno10", "Find X5"],
      metric: ["Шт."],
      compare: ["WoW"],
      lfl: ["LFL выкл"],
    },
    supervisor: {
      scope: ["Юг"],
      period: ["Текущая неделя"],
      timeGrain: ["Неделя"],
      models: ["Reno10"],
      metric: ["₸"],
      compare: ["WoW"],
      lfl: ["LFL вкл"],
    },
  },
};

const filtersConfig = {
  office: [
    {
      key: "scope",
      label: "Охват",
      multi: false,
      options: ["Все", "Сеть", "Магазин"],
    },
    {
      key: "period",
      label: "Период",
      multi: false,
      options: [
        "Текущая неделя",
        "Текущий месяц",
        "Этот квартал",
        "Произвольный",
      ],
    },
    {
      key: "timeGrain",
      label: "Гранулярность",
      multi: false,
      options: ["День", "Неделя", "Месяц", "Год"],
    },
    {
      key: "models",
      label: "Модели",
      multi: true,
      options: ["Reno10", "Find X5", "A78", "A17", "Find N3"],
    },
    {
      key: "metric",
      label: "Метрика",
      multi: false,
      options: ["Шт.", "₸", "Achv%", "Bonus"],
    },
    {
      key: "compare",
      label: "Сравнение",
      multi: true,
      options: ["WoW", "MoM", "YoY"],
    },
    {
      key: "lfl",
      label: "LFL",
      multi: false,
      options: ["LFL вкл", "LFL выкл"],
    },
  ],
  supervisor: [
    {
      key: "scope",
      label: "Регион",
      multi: false,
      options: ["Юг", "Центр"],
    },
    {
      key: "period",
      label: "Период",
      multi: false,
      options: ["Текущая неделя", "Текущий месяц"],
    },
    {
      key: "timeGrain",
      label: "Гранулярность",
      multi: false,
      options: ["Неделя", "Месяц"],
    },
    {
      key: "models",
      label: "Модели",
      multi: true,
      options: ["Reno10", "A78", "A58"],
    },
    {
      key: "metric",
      label: "Метрика",
      multi: false,
      options: ["₸", "Achv%"],
    },
    {
      key: "compare",
      label: "Сравнение",
      multi: true,
      options: ["WoW", "MoM"],
    },
    {
      key: "lfl",
      label: "LFL",
      multi: false,
      options: ["LFL вкл", "LFL выкл"],
    },
  ],
};

const kpiData = {
  admin: [
    { title: "Пользователи", value: "128", note: "активны за 7 дней" },
    { title: "Ошибки API", value: "3", note: "за 24 часа", variant: "danger" },
    { title: "Синхронизации", value: "12", note: "выполнено сегодня" },
  ],
  office: [
    { title: "План месяца", value: "₸ 180M", note: "Офис установил" },
    { title: "Факт", value: "₸ 132M", note: "73% выполнения" },
    { title: "Бонусный фонд", value: "₸ 8.4M", note: "доступно" },
  ],
  supervisor: [
    { title: "Регион Юг", value: "₸ 72M", note: "4 сети" },
    { title: "Топ магазин", value: "Mega Alma", note: "₸ 12.5M" },
    { title: "Промоутеры", value: "38", note: "активны" },
  ],
  promoter: [
    { title: "План месяца", value: "₸ 2.4M", note: "установил офис" },
    { title: "Факт", value: "₸ 1.86M", note: "78% выполнено" },
    { title: "Бонус к выплате", value: "₸ 180k", note: "после апрува" },
  ],
  trainer: [
    { title: "Сессии", value: "12", note: "в этом месяце" },
    { title: "Участники", value: "84", note: "план/факт совпал" },
    { title: "Оценка", value: "4.8", note: "средний рейтинг" },
  ],
};

const tableData = {
  users: [
    {
      name: "Мария Токтарова",
      role: "office",
      region: "HQ",
      lastLogin: "2024-04-10 09:22",
      status: "active",
    },
    {
      name: "Ержан Абдрахман",
      role: "supervisor",
      region: "Юг",
      lastLogin: "2024-04-10 08:14",
      status: "active",
    },
    {
      name: "Нурия Бахыт",
      role: "promoter",
      region: "Алматы",
      lastLogin: "2024-04-09 18:33",
      status: "pending",
    },
    {
      name: "Адиль Серик",
      role: "trainer",
      region: "HQ",
      lastLogin: "2024-04-08 11:08",
      status: "active",
    },
    {
      name: "Айгерим Иса",
      role: "admin",
      region: "HQ",
      lastLogin: "2024-04-10 10:40",
      status: "active",
    },
  ],
  bonuses: [
    {
      store: "Mega Alma",
      promoter: "Нурия Бахыт",
      plan: "₸ 420k",
      fact: "₸ 480k",
      achv: "114%",
      bonus: "₸ 65k",
    },
    {
      store: "Sulpak Esentai",
      promoter: "Еламан Кайрат",
      plan: "₸ 380k",
      fact: "₸ 322k",
      achv: "85%",
      bonus: "₸ 28k",
    },
    {
      store: "Mechta Dostyk",
      promoter: "Айдана Сеит",
      plan: "₸ 300k",
      fact: "₸ 280k",
      achv: "93%",
      bonus: "₸ 24k",
    },
  ],
  "promoter-bonuses": [
    {
      month: "Январь",
      plan: "₸ 2.0M",
      fact: "₸ 1.8M",
      achv: "90%",
      bonus: "₸ 150k",
    },
    {
      month: "Февраль",
      plan: "₸ 2.2M",
      fact: "₸ 2.05M",
      achv: "93%",
      bonus: "₸ 165k",
    },
    {
      month: "Март",
      plan: "₸ 2.4M",
      fact: "₸ 1.86M",
      achv: "78%",
      bonus: "₸ 180k",
    },
  ],
  training: [
    {
      date: "12.04.2024",
      city: "Алматы",
      topic: "Reno10 камера",
      attendees: "16",
      status: "Запланировано",
    },
    {
      date: "18.04.2024",
      city: "Астана",
      topic: "Финальный апсейл",
      attendees: "18",
      status: "Подтверждено",
    },
    {
      date: "22.04.2024",
      city: "Шымкент",
      topic: "Find X5 премиум",
      attendees: "12",
      status: "Формируется",
    },
  ],
};

const lazyCityData = [
  {
    city: "Алматы",
    network: "Sulpak",
    stores: "18",
    promoters: "24",
    status: "Работает",
  },
  {
    city: "Астана",
    network: "Mechta",
    stores: "12",
    promoters: "16",
    status: "Работает",
  },
  {
    city: "Шымкент",
    network: "Technodom",
    stores: "9",
    promoters: "11",
    status: "Нужен выезд",
  },
  {
    city: "Караганда",
    network: "Mechta",
    stores: "6",
    promoters: "7",
    status: "Работает",
  },
];

const chartCopy = {
  overview: {
    day: "График: продажи по дням. Второй показатель ASP включается опцией.",
    week: "График: недельные продажи. Доступен сравнительный анализ.",
    month: "График: продажи по месяцам. Отображает накопленный итог.",
  },
  models: "Сравнение до 5 моделей. Цвета соответствуют легенде.",
  promoter: "Личные продажи по дням с плановой линией.",
};

const comparisonState = [
  { label: "WoW", value: "+4.2%", trend: "up" },
  { label: "MoM", value: "+1.8%", trend: "up" },
  { label: "YoY", value: "−3.4%", trend: "down" },
];

const statusData = {
  api: { value: "OK", note: "99.9% uptime" },
  db: { value: "OK", note: "Latency 22ms" },
  bi: { value: "OK", note: "Metabase green" },
};

let activePopover = null;
let activePopoverContext = null;
let activePopoverKey = null;
let activeModalTrigger = null;
let focusTrapListener = null;

const selectors = {
  dashboards: document.querySelectorAll("[data-role-panel]"),
  roleTabs: document.querySelectorAll(".role-tabs .tab-button"),
  kpiContainers: document.querySelectorAll("[data-kpi]"),
  tables: document.querySelectorAll("table.responsive-table"),
  filterRegions: document.querySelectorAll("[data-filter-context]"),
  analyticsTabs: document.querySelectorAll(".sub-tabs"),
  analyticsPanels: document.querySelectorAll("[data-panel]"),
  grainButtons: document.querySelectorAll(".grain-button"),
  secondaryToggle: document.querySelector("[data-secondary-axis]"),
  chartPlaceholders: document.querySelectorAll("[data-chart]"),
  comparisons: document.querySelector("[data-comparisons]"),
  legend: document.querySelector("[data-legend]"),
  modal: document.querySelector("[data-modal]"),
  modalBody: document.querySelector("[data-modal-body]"),
  modalBackdrop: document.querySelector("[data-modal-backdrop]"),
  lazySections: document.querySelectorAll("[data-lazy]")
};

document.addEventListener("DOMContentLoaded", () => {
  renderAllKpis();
  populateTables();
  enhanceTables();
  hydrateStatuses();
  setupRoleTabs();
  setupAnalyticsTabs();
  setupFilters();
  setupTableFilters();
  setupGrainSwitch();
  setupComparisons();
  setupLegend();
  setupMapMarkers();
  setupLazyLoading();
  setupModalClose();
});

function renderAllKpis() {
  selectors.kpiContainers.forEach((container) => {
    const key = container.dataset.kpi;
    container.innerHTML = "";
    kpiData[key].forEach((item) => {
      const card = document.createElement("article");
      card.className = "kpi-card";
      if (item.variant) {
        card.dataset.variant = item.variant;
      }
      card.innerHTML = `
        <h3>${item.title}</h3>
        <p class="kpi-value">${item.value}</p>
        <p class="kpi-note">${item.note}</p>
      `;
      container.append(card);
    });
  });
}

function populateTables() {
  Object.entries(tableData).forEach(([key, rows]) => {
    const table = document.querySelector(`table[data-table="${key}"] tbody`);
    if (!table) return;
    table.innerHTML = "";
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      Object.values(row).forEach((value) => {
        const td = document.createElement("td");
        td.textContent = value;
        tr.append(td);
      });
      table.append(tr);
    });
  });
}

function enhanceTables() {
  selectors.tables.forEach((table) => {
    const headers = Array.from(table.querySelectorAll("thead th"));
    const rows = table.querySelectorAll("tbody tr");
    rows.forEach((row) => {
      Array.from(row.children).forEach((cell, index) => {
        const label = headers[index]?.textContent?.trim() ?? "";
        const priority = headers[index]?.dataset.priority ?? "primary";
        cell.setAttribute("data-label", label);
        cell.dataset.priority = priority;
      });
    });
    headers.forEach((th, index) => {
      th.addEventListener("click", () => handleSort(table, index));
    });
  });
}

function handleSort(table, columnIndex) {
  if (window.matchMedia("(max-width: 768px)").matches) {
    return; // disable sorting on stacked view
  }
  const tbody = table.querySelector("tbody");
  const rows = Array.from(tbody.querySelectorAll("tr"));
  const isNumeric = rows.every((row) => {
    const text = row.children[columnIndex]?.textContent?.replace(/[^0-9.-]/g, "");
    return text !== "";
  });
  const current = table.dataset.sortColumn === String(columnIndex) ? table.dataset.sortDir : "asc";
  const nextDir = current === "asc" ? "desc" : "asc";
  const sorted = rows.sort((a, b) => {
    const aText = a.children[columnIndex]?.textContent ?? "";
    const bText = b.children[columnIndex]?.textContent ?? "";
    if (isNumeric) {
      const aNum = parseFloat(aText.replace(/[^0-9.-]/g, "")) || 0;
      const bNum = parseFloat(bText.replace(/[^0-9.-]/g, "")) || 0;
      return nextDir === "asc" ? aNum - bNum : bNum - aNum;
    }
    return nextDir === "asc" ? aText.localeCompare(bText) : bText.localeCompare(aText);
  });
  tbody.innerHTML = "";
  sorted.forEach((row) => tbody.append(row));
  table.dataset.sortColumn = String(columnIndex);
  table.dataset.sortDir = nextDir;
}

function setupRoleTabs() {
  selectors.roleTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const role = tab.dataset.role;
      if (role === state.currentRole) return;
      state.currentRole = role;
      selectors.roleTabs.forEach((btn) => btn.classList.toggle("is-active", btn === tab));
      selectors.dashboards.forEach((panel) => {
        panel.classList.toggle("is-hidden", panel.dataset.rolePanel !== role);
      });
      document.getElementById("main").focus();
    });
  });
}

function setupAnalyticsTabs() {
  selectors.analyticsTabs.forEach((nav) => {
    const buttons = nav.querySelectorAll(".sub-tab-button");
    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        buttons.forEach((btn) => btn.classList.toggle("is-active", btn === button));
        const target = button.dataset.target;
        const parent = nav.closest(".analytics");
        parent.querySelectorAll("[data-panel]").forEach((panel) => {
          panel.classList.toggle("is-hidden", panel.dataset.panel !== target);
        });
      });
    });
  });
}

function setupFilters() {
  selectors.filterRegions.forEach((region) => {
    const context = region.dataset.filterContext;
    const controlsContainer = region.querySelector("[data-filter-controls]");
    const chipsContainer = region.querySelector("[data-filter-chips]");
    controlsContainer.innerHTML = "";
    filtersConfig[context].forEach((filter) => {
      const trigger = document.createElement("button");
      trigger.type = "button";
      trigger.className = "filter-trigger";
      trigger.dataset.filterKey = filter.key;
      trigger.textContent = filter.label;
      trigger.addEventListener("click", (event) => {
        event.stopPropagation();
        togglePopover(event.currentTarget, context, filter);
      });
      controlsContainer.append(trigger);
    });
    updateFilterChips(context, chipsContainer);
  });

  document.addEventListener("click", (event) => {
    if (
      activePopover &&
      !activePopover.contains(event.target) &&
      event.target !== activePopover.trigger
    ) {
      activePopover.remove();
      activePopover = null;
      activePopoverContext = null;
      activePopoverKey = null;
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && activePopover) {
      activePopover.remove();
      activePopover = null;
      activePopoverContext = null;
      activePopoverKey = null;
    }
  });

  document.querySelectorAll("[data-action=\"clear-filters\"]").forEach((button) => {
    button.addEventListener("click", () => {
      const context = button.closest("[data-filter-context]")?.dataset.filterContext;
      if (!context) return;
      filtersConfig[context].forEach((filter) => {
        state.filters[context][filter.key] = filter.multi ? [] : [];
      });
      if (activePopover) {
        activePopover.remove();
        activePopover = null;
        activePopoverContext = null;
        activePopoverKey = null;
      }
      updateFilterChips(context, button.closest("[data-filter-context]").querySelector("[data-filter-chips]"));
    });
  });
}

function togglePopover(trigger, context, filter) {
  if (
    activePopover &&
    activePopoverContext === context &&
    activePopoverKey === filter.key
  ) {
    activePopover.remove();
    activePopover = null;
    activePopoverContext = null;
    activePopoverKey = null;
    return;
  }

  if (activePopover) {
    activePopover.remove();
  }

  const popover = document.createElement("div");
  popover.className = "filter-popover";
  popover.trigger = trigger;

  const renderOptions = () => {
    popover.innerHTML = "";
    filter.options.forEach((option) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "filter-option";
      button.textContent = option;
      const current = state.filters[context][filter.key] ?? [];
      button.setAttribute("aria-pressed", String(current.includes(option)));
      button.addEventListener("click", () => {
        applyFilterSelection(context, filter, option);
        updateFilterChips(
          context,
          trigger.closest("[data-filter-context]").querySelector("[data-filter-chips]")
        );
        renderOptions();
      });
      popover.append(button);
    });
  };

  renderOptions();
  document.body.append(popover);
  const place = () => {
    const rect = trigger.getBoundingClientRect();
    const top = rect.bottom + window.scrollY + 8;
    const left = rect.left + window.scrollX;
    const maxLeft = window.innerWidth - popover.offsetWidth - 16;
    popover.style.top = `${top}px`;
    popover.style.left = `${Math.max(12, Math.min(left, maxLeft))}px`;
  };
  requestAnimationFrame(place);
  activePopover = popover;
  activePopoverContext = context;
  activePopoverKey = filter.key;
}

function applyFilterSelection(context, filter, option) {
  const bucket = state.filters[context][filter.key] ?? [];
  if (filter.multi) {
    const index = bucket.indexOf(option);
    if (index > -1) {
      bucket.splice(index, 1);
    } else {
      bucket.push(option);
    }
    state.filters[context][filter.key] = bucket;
  } else {
    state.filters[context][filter.key] = bucket[0] === option ? [] : [option];
  }
}

function updateFilterChips(context, container) {
  container.innerHTML = "";
  const filters = state.filters[context];
  Object.entries(filters).forEach(([key, values]) => {
    values.filter(Boolean).forEach((value) => {
      const chip = document.createElement("span");
      chip.className = "filter-chip";
      chip.innerHTML = `${value} <button type="button" aria-label="Убрать ${value}">×</button>`;
      chip.querySelector("button").addEventListener("click", () => {
        state.filters[context][key] = state.filters[context][key].filter((item) => item !== value);
        updateFilterChips(context, container);
      });
      container.append(chip);
    });
  });
}

function setupTableFilters() {
  document.querySelectorAll(".mobile-table-filter input").forEach((input) => {
    if (input.dataset.bound === "true") return;
    const tableKey = input.closest(".mobile-table-filter").dataset.filterFor;
    const table = document.querySelector(`table[data-table="${tableKey}"] tbody`);
    input.addEventListener("input", () => {
      const query = input.value.toLowerCase();
      if (!table) return;
      Array.from(table.querySelectorAll("tr")).forEach((row) => {
        const visible = row.textContent.toLowerCase().includes(query);
        row.style.display = visible ? "" : "none";
      });
    });
    input.dataset.bound = "true";
  });
}

function setupGrainSwitch() {
  selectors.grainButtons.forEach((button) => {
    button.addEventListener("click", () => {
      selectors.grainButtons.forEach((btn) => btn.classList.toggle("is-active", btn === button));
      state.chart.grain = button.dataset.grain;
      renderChartCopy();
    });
  });
  if (selectors.secondaryToggle) {
    selectors.secondaryToggle.addEventListener("change", (event) => {
      state.chart.secondaryAxis = Boolean(event.target.checked);
      renderChartCopy();
    });
  }
  renderChartCopy();
}

function renderChartCopy() {
  selectors.chartPlaceholders.forEach((placeholder) => {
    const key = placeholder.dataset.chart;
    if (key === "overview") {
      const grainCopy = chartCopy.overview[state.chart.grain];
      const axis = state.chart.secondaryAxis ? " Включена вторая ось ASP." : "";
      placeholder.textContent = `${grainCopy}${axis}`;
    } else {
      placeholder.textContent = chartCopy[key];
    }
  });
}

function setupComparisons() {
  if (!selectors.comparisons) return;
  selectors.comparisons.innerHTML = "";
  comparisonState.forEach((item) => {
    const chip = document.createElement("span");
    chip.className = "comparison-chip";
    chip.dataset.trend = item.trend;
    chip.textContent = `${item.label}: ${item.value}`;
    selectors.comparisons.append(chip);
  });
}

function setupLegend() {
  if (!selectors.legend) return;
  const colors = ["#22c55e", "#38bdf8", "#f97316", "#a855f7", "#facc15"];
  const models = filtersConfig.office.find((item) => item.key === "models").options.slice(0, 5);
  selectors.legend.innerHTML = "";
  models.forEach((model, index) => {
    const item = document.createElement("div");
    item.className = "legend-item";
    item.innerHTML = `
      <span class="legend-swatch" style="background:${colors[index % colors.length]}"></span>
      <span>${model}</span>
    `;
    selectors.legend.append(item);
  });
}

function setupMapMarkers() {
  const markers = document.querySelectorAll(".map-marker");
  markers.forEach((marker) => {
    marker.setAttribute("tabindex", "0");
    const showDetails = (event) => {
      event.preventDefault();
      const city = marker.dataset.city;
      const region = marker.dataset.region;
      openModal(
        `<p><strong>${city}</strong></p><p>Регион: ${region}</p><p>Оборот за месяц: ₸ ${(Math.random() * 12 + 3).toFixed(1)}M</p>`,
        `Магазины · ${city}`,
        marker
      );
    };
    marker.addEventListener("click", showDetails);
    marker.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        showDetails(event);
      }
    });
  });

  const isTouch = matchMedia("(pointer: coarse)").matches;
  if (isTouch) {
    markers.forEach((marker) => {
      marker.classList.add("touch-target");
    });
  }
}

function setupLazyLoading() {
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        if (entry.target.dataset.lazy === "cities") {
          renderCityTable(entry.target.querySelector("[data-lazy-target]"));
        }
        obs.unobserve(entry.target);
      }
    });
  }, {
    rootMargin: "200px 0px",
  });
  selectors.lazySections.forEach((section) => observer.observe(section));
}

function renderCityTable(container) {
  const template = document.getElementById("city-table-template");
  if (!template) return;
  const fragment = template.content.cloneNode(true);
  const tbody = fragment.querySelector("tbody");
  lazyCityData.forEach((row) => {
    const tr = document.createElement("tr");
    Object.values(row).forEach((value) => {
      const td = document.createElement("td");
      td.textContent = value;
      tr.append(td);
    });
    tbody.append(tr);
  });
  container.innerHTML = "";
  container.append(fragment);
  enhanceTables();
  setupTableFilters();
}

function hydrateStatuses() {
  Object.entries(statusData).forEach(([key, payload]) => {
    const valueEl = document.querySelector(`[data-status="${key}"]`);
    if (!valueEl) return;
    valueEl.textContent = payload.value;
    const noteEl = valueEl.nextElementSibling;
    if (noteEl) {
      noteEl.textContent = payload.note;
    }
  });
}

function setupModalClose() {
  const modal = selectors.modal;
  const closeButtons = modal.querySelectorAll("[data-modal-close]");
  closeButtons.forEach((button) => button.addEventListener("click", closeModal));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hasAttribute("hidden")) {
      closeModal();
    }
  });
}

function openModal(content, title, trigger) {
  const modal = selectors.modal;
  const backdrop = selectors.modalBackdrop;
  selectors.modalBody.innerHTML = content;
  modal.querySelector("#modal-title").textContent = title;
  activeModalTrigger = trigger instanceof HTMLElement ? trigger : null;
  const isSheet = window.matchMedia("(max-width: 768px)").matches;
  modal.dataset.mode = isSheet ? "sheet" : "dialog";
  modal.setAttribute("open", "");
  modal.removeAttribute("hidden");
  backdrop.hidden = false;
  backdrop.dataset.active = "true";
  document.body.style.overflow = "hidden";
  const focusable = modal.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  const trap = (event) => {
    if (event.key !== "Tab") return;
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };
  focusTrapListener = trap;
  document.addEventListener("keydown", focusTrapListener);
  if (first) first.focus();
}

function closeModal() {
  const modal = selectors.modal;
  const backdrop = selectors.modalBackdrop;
  modal.setAttribute("hidden", "");
  modal.removeAttribute("open");
  modal.removeAttribute("data-mode");
  backdrop.hidden = true;
  backdrop.dataset.active = "false";
  selectors.modalBody.innerHTML = "";
  document.body.style.overflow = "";
  if (focusTrapListener) {
    document.removeEventListener("keydown", focusTrapListener);
    focusTrapListener = null;
  }
  if (activeModalTrigger instanceof HTMLElement) {
    activeModalTrigger.focus();
  }
}
