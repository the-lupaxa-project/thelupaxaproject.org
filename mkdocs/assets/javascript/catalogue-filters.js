/**
 * Searchable catalogue filters for projects, organisations, and policies.
 */

(() => {
  "use strict";

  const { onPageRender } = window.LupaxaPageLifecycle;

  const URL_PARAM_SEARCH = "search";
  const URL_PARAM_CATEGORY = "category";
  const URL_PARAM_ORG = "org";
  const URL_PARAM_STATUS = "status";
  const URL_PARAM_SORT = "sort";
  const SORT_NEWEST = "newest";
  const SORT_ALPHA = "alpha";
  const FALLBACK_ORG = "Other";
  const CATALOGUE_LOCALE = "en-GB";
  /** Shared with article-pager.js — filtered prev/next sequence. */
  const ARTICLE_PAGER_STORAGE_KEY = "lupaxa.articlePager";

  /**
   * Build catalogue selector config from a short id prefix.
   *
   * @param {Object} options
   * @param {string} options.id
   * @param {string} options.singular
   * @param {string} options.plural
   * @param {boolean} [options.organisation=false]
   * @param {boolean} [options.status=false]
   * @param {boolean} [options.sort=false]
   * @returns {Object}
   */
  function catalogueConfig({
    id,
    singular,
    plural,
    organisation = false,
    status = false,
    sort = false,
  }) {
    const config = {
      singular,
      plural,
      sort,
      filtersSelector: `[data-${id}-filters]`,
      catalogueSelector: `[data-${id}-catalogue]`,
      searchSelector: `[data-${id}-search]`,
      categorySelector: `[data-${id}-category]`,
      clearSelector: `[data-${id}-clear]`,
      summarySelector: `[data-${id}-summary]`,
      emptySelector: `[data-${id}-empty]`,
    };

    if (organisation) {
      config.organisationSelector = `[data-${id}-organisation]`;
    }

    if (status) {
      config.statusSelector = `[data-${id}-status]`;
      // dataset key for data-{id}-status on toggle buttons (e.g. policyStatus)
      config.statusDatasetKey = `${id}Status`;
    }

    if (sort) {
      config.sortSelector = `[data-${id}-sort]`;
      config.sortDatasetKey = `${id}Sort`;
    }

    return config;
  }

  /**
   * Whether the current URL already carries a catalogue filter or sort.
   *
   * @returns {boolean}
   */
  function urlHasFilterParams() {
    const params = new URLSearchParams(window.location.search);

    return (
      params.has(URL_PARAM_SEARCH) ||
      params.has(URL_PARAM_CATEGORY) ||
      params.has(URL_PARAM_ORG) ||
      params.has(URL_PARAM_STATUS) ||
      params.has(URL_PARAM_SORT)
    );
  }

  /**
   * Expand or collapse a catalogue filter panel and keep the toggle in sync.
   *
   * @param {HTMLElement} filterPanel
   * @param {boolean} expanded
   */
  function setFilterPanelExpanded(filterPanel, expanded) {
    const button = filterPanel.querySelector("[data-filter-expand]");

    filterPanel.classList.toggle("filter-panel--expanded", expanded);

    if (!(button instanceof HTMLButtonElement)) {
      return;
    }

    button.setAttribute("aria-expanded", expanded ? "true" : "false");

    const label = button.querySelector(".filter-panel-expand__label");
    const labelText = expanded ? "Hide Filters" : "Show Filters";

    if (label) {
      label.textContent = labelText;
    } else {
      button.textContent = labelText;
    }
  }

  /**
   * Show the filter controls after a card pill, banner, or logo applies a
   * filter, so the active selection is visible.
   *
   * @param {HTMLElement} filterPanel
   */
  function revealFilterPanel(filterPanel) {
    setFilterPanelExpanded(filterPanel, true);
    filterPanel.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
    });
  }

  /**
   * Collapsible filter toolbar for every catalogue viewport.
   *
   * Panels start collapsed (Filters + summary only). Expand when the
   * button is pressed, when the URL already carries filter/sort
   * parameters, or when a card control applies a filter.
   *
   * @param {HTMLElement} filterPanel
   */
  function initialiseFilterCollapse(filterPanel) {
    const button = filterPanel.querySelector("[data-filter-expand]");

    if (!(button instanceof HTMLButtonElement)) {
      return;
    }

    button.addEventListener("click", () => {
      filterPanel.dataset.collapseUserToggled = "true";
      setFilterPanelExpanded(
        filterPanel,
        !filterPanel.classList.contains("filter-panel--expanded"),
      );
    });

    setFilterPanelExpanded(filterPanel, urlHasFilterParams());
  }

  /**
   * Convert text into a consistent comparison value.
   *
   * @param {string} value
   * @returns {string}
   */
  function normaliseCatalogueValue(value) {
    return String(value ?? "")
      .toLocaleLowerCase(CATALOGUE_LOCALE)
      .replace(/\s+/g, " ")
      .trim();
  }

  /**
   * Add alphabetically sorted options to a select element.
   *
   * @param {HTMLSelectElement} select
   * @param {Map<string, string>} options
   */
  function addCatalogueOptions(select, options) {
    Array.from(options.entries())
      .sort((left, right) =>
        left[1].localeCompare(right[1], CATALOGUE_LOCALE),
      )
      .forEach(([value, label]) => {
        const option = document.createElement("option");

        option.value = value;
        option.textContent = label;

        select.append(option);
      });
  }

  /**
   * Return the categories attached to a catalogue card.
   *
   * @param {HTMLElement} card
   * @returns {{ values: string[], labels: string[] }}
   */
  function getCatalogueCategories(card) {
    const labels = Array.from(
      card.querySelectorAll(".catalogue-category"),
    )
      .map((category) => category.textContent?.trim() || "")
      .filter(Boolean);

    return {
      labels,
      values: labels.map(normaliseCatalogueValue),
    };
  }

  /**
   * Turn an organisation logo into a link to the Projects catalogue.
   *
   * The organisation is passed through the "org" URL parameter so that the
   * Projects page opens with the matching organisation filter selected.
   *
   * @param {HTMLImageElement} logo
   * @param {string} organisation
   * @param {string} projectsPath
   */
  function addOrganisationProjectLink(
    logo,
    organisation,
    projectsPath,
  ) {
    if (
      !logo ||
      !organisation ||
      logo.closest("[data-organisation-project-link]")
    ) {
      return;
    }

    const url = new URL(projectsPath, window.location.href);

    url.searchParams.set(URL_PARAM_ORG, organisation);

    const link = document.createElement("a");

    link.href = url.href;
    link.dataset.organisationProjectLink = "";
    link.setAttribute(
      "aria-label",
      `View projects from ${organisation}`,
    );

    logo.replaceWith(link);
    link.append(logo);
  }

  /**
   * Persist the visible articles sequence for filtered prev/next paging.
   *
   * Cleared when no filters are active and sort is A–Z, so article pages
   * use the full build-time A–Z pager again. Kept whenever a filter is
   * active or the Newest sort is selected, since both change the visible
   * order relative to that build-time pager.
   *
   * @param {Object} config
   * @param {Array<{ element: HTMLElement }>} cardData
   * @param {{
   *   searchTerm: string,
   *   selectedCategory: string,
   *   selectedOrganisation: string,
   *   selectedStatus: string
   * }} filters
   * @param {string} [activeSort]
   */
  function syncArticlePagerSequence(
    config,
    cardData,
    filters,
    activeSort,
  ) {
    if (config.singular !== "article") {
      return;
    }

    const hasFilter =
      filters.searchTerm !== "" ||
      filters.selectedCategory !== "" ||
      filters.selectedOrganisation !== "" ||
      filters.selectedStatus !== "";

    const needsCustomOrder =
      hasFilter || activeSort === SORT_NEWEST;

    if (!needsCustomOrder) {
      sessionStorage.removeItem(ARTICLE_PAGER_STORAGE_KEY);
      return;
    }

    const articlesBase = articleCatalogueBasePath();

    const sequence = cardData
      .filter((card) => !card.element.hidden)
      .map((card) => {
        const link = card.element.querySelector(
          ":scope > p:first-child a[href]",
        );

        if (!(link instanceof HTMLAnchorElement)) {
          return null;
        }

        const title = link.textContent?.trim() || "";
        const slug = articleSlugFromHref(
          link.getAttribute("href") || "",
        );

        if (!title || !slug) {
          return null;
        }

        return {
          title,
          slug,
          url: `${articlesBase}/${slug}/`,
        };
      })
      .filter(Boolean);

    if (sequence.length === 0) {
      sessionStorage.removeItem(ARTICLE_PAGER_STORAGE_KEY);
      return;
    }

    sessionStorage.setItem(
      ARTICLE_PAGER_STORAGE_KEY,
      JSON.stringify({ sequence }),
    );
  }

  /**
   * Base path for article pages (handles optional site prefix).
   *
   * @returns {string}
   */
  function articleCatalogueBasePath() {
    const path = window.location.pathname;
    const match = path.match(/^(.*?\/articles)(?:\/|$)/);

    return match ? match[1].replace(/\/+$/, "") : "/articles";
  }

  /**
   * Article slug from a catalogue href such as "cli-design/".
   *
   * @param {string} href
   * @returns {string}
   */
  function articleSlugFromHref(href) {
    const cleaned = String(href || "")
      .split(/[?#]/)[0]
      .replace(/\/+$/, "")
      .replace(/\.html$/i, "");

    if (!cleaned) {
      return "";
    }

    const parts = cleaned.split("/").filter(Boolean);
    return parts[parts.length - 1] || "";
  }

  /**
   * Remove catalogue filter parameters from the current URL.
   */
  function clearCatalogueUrlParameters() {
    const url = new URL(window.location.href);

    url.searchParams.delete(URL_PARAM_SEARCH);
    url.searchParams.delete(URL_PARAM_CATEGORY);
    url.searchParams.delete(URL_PARAM_ORG);
    url.searchParams.delete(URL_PARAM_STATUS);

    window.history.replaceState(
      window.history.state,
      "",
      `${url.pathname}${url.search}${url.hash}`,
    );
  }

  /**
   * Remove temporary options created for URL-supplied filter values.
   *
   * @param {HTMLSelectElement} select
   */
  function removeUrlFilterOptions(select) {
    select
      .querySelectorAll("option[data-url-filter-option]")
      .forEach((option) => {
        option.remove();
      });
  }

  /**
   * Initialise one searchable catalogue.
   *
   * @param {Object} config
   */
  function initialiseCatalogue(config) {
    const filterPanel = document.querySelector(
      config.filtersSelector,
    );
    const catalogue = document.querySelector(
      config.catalogueSelector,
    );

    if (!filterPanel || !catalogue) {
      return;
    }

    if (filterPanel.dataset.initialised === "true") {
      if (urlHasFilterParams()) {
        setFilterPanelExpanded(filterPanel, true);
      }

      return;
    }

    const searchInput = filterPanel.querySelector(
      config.searchSelector,
    );
    const categorySelect = filterPanel.querySelector(
      config.categorySelector,
    );
    const clearButton = filterPanel.querySelector(
      config.clearSelector,
    );
    const summary = filterPanel.querySelector(
      config.summarySelector,
    );
    const emptyState = document.querySelector(
      config.emptySelector,
    );

    const organisationSelect = config.organisationSelector
      ? filterPanel.querySelector(config.organisationSelector)
      : null;
    const statusNodes = config.statusSelector
      ? Array.from(
          filterPanel.querySelectorAll(config.statusSelector),
        )
      : [];
    const statusSelect =
      statusNodes.length === 1 &&
      statusNodes[0] instanceof HTMLSelectElement
        ? statusNodes[0]
        : null;
    const statusButtons = statusSelect ? [] : statusNodes;
    const hasStatusControl = Boolean(statusSelect) ||
      statusButtons.length > 0;

    if (
      !searchInput ||
      !categorySelect ||
      !clearButton ||
      !summary ||
      (config.organisationSelector && !organisationSelect) ||
      (config.statusSelector && !hasStatusControl)
    ) {
      return;
    }

    filterPanel.dataset.initialised = "true";
    initialiseFilterCollapse(filterPanel);

    const cards = Array.from(
      catalogue.querySelectorAll(":scope > ul > li"),
    );

    const categoryOptions = new Map();

    const cardData = cards.map((card) => {
      const categories = getCatalogueCategories(card);
      const logo = card.querySelector(".catalogue-logo");
      const banner = card.querySelector(".catalogue-banner");

      const organisationLabel =
        logo?.dataset.organisation?.trim() || "";

      const organisationValue = normaliseCatalogueValue(
        organisationLabel,
      );

      const statusValue = normaliseCatalogueValue(
        banner?.dataset.bannerStatus || "",
      );
      const statusLabel =
        banner?.dataset.bannerLabel?.trim() ||
        banner?.querySelector(".catalogue-banner__text")
          ?.textContent?.trim() ||
        "";

      categories.labels.forEach((label, index) => {
        categoryOptions.set(categories.values[index], label);
      });

      const titleNode = card.querySelector(
        ":scope > h3, :scope > p:first-child a[href], :scope > p:first-child strong",
      );

      return {
        element: card,
        categories: categories.values,
        organisation: organisationSelect
          ? organisationValue ||
            normaliseCatalogueValue(FALLBACK_ORG)
          : "",
        status: hasStatusControl ? statusValue : "",
        searchableText: normaliseCatalogueValue(
          [
            card.textContent || "",
            organisationLabel,
            statusLabel,
            ...categories.labels,
          ].join(" "),
        ),
        publishDate:
          logo?.dataset.releasedDate?.trim() ||
          logo?.dataset.publishDate?.trim() ||
          "",
        title:
          logo?.dataset.name?.trim() ||
          (titleNode?.textContent || "").trim(),
      };
    });

    addCatalogueOptions(categorySelect, categoryOptions);

    // Organisation and status options are fixed in the filter panel
    // markup (every published organisation; lifecycle presets plus
    // Stable for projects). Only categories come from visible cards.

    const sortButtons = config.sort
      ? filterPanel.querySelectorAll(config.sortSelector)
      : [];

    let activeSort = SORT_ALPHA;
    // Segmented status toggle (articles): "" = All, "new" = New.
    let activeStatus = "";

    /**
     * Read the sort value from a segmented sort button.
     *
     * @param {HTMLElement} button
     * @returns {string}
     */
    const sortFromButton = (button) =>
      String(button.dataset[config.sortDatasetKey] ?? "");

    /**
     * Read the requested sort mode from the URL (defaults to A–Z).
     *
     * @returns {string}
     */
    const readSortFromUrl = () => {
      const value = new URLSearchParams(
        window.location.search,
      ).get(URL_PARAM_SORT);

      return value === SORT_NEWEST ? SORT_NEWEST : SORT_ALPHA;
    };

    /**
     * Reflect the active sort on the segmented button group.
     *
     * @param {string} sort
     */
    const setSortPressed = (sort) => {
      sortButtons.forEach((button) => {
        const isActive = sortFromButton(button) === sort;

        button.setAttribute(
          "aria-pressed",
          isActive ? "true" : "false",
        );
      });
    };

    /**
     * Map a status-toggle button dataset value to the filter key.
     *
     * @param {HTMLElement} button
     * @returns {string}
     */
    const statusFromButton = (button) => {
      const raw = String(
        button.dataset[config.statusDatasetKey] ?? "",
      );

      if (!raw || raw === "all") {
        return "";
      }

      return normaliseCatalogueValue(raw);
    };

    /**
     * Reflect the active status on the segmented button group.
     *
     * @param {string} status
     */
    const setStatusPressed = (status) => {
      statusButtons.forEach((button) => {
        const isActive = statusFromButton(button) === status;

        button.setAttribute(
          "aria-pressed",
          isActive ? "true" : "false",
        );
      });
    };

    /**
     * Compare two cards for the active sort order.
     *
     * @param {Object} left
     * @param {Object} right
     * @returns {number}
     */
    const compareCards = (left, right) => {
      if (activeSort === SORT_NEWEST) {
        const leftDate = left.publishDate || "";
        const rightDate = right.publishDate || "";

        if (leftDate !== rightDate) {
          if (!leftDate) {
            return 1;
          }

          if (!rightDate) {
            return -1;
          }

          return rightDate.localeCompare(leftDate);
        }
      }

      return left.title.localeCompare(right.title, CATALOGUE_LOCALE, {
        sensitivity: "base",
      });
    };

    /**
     * Reorder the catalogue DOM (and cardData) to match the active sort.
     */
    const applyCardOrder = () => {
      const list = catalogue.querySelector(":scope > ul");

      if (!list) {
        return;
      }

      const ordered = [...cardData].sort(compareCards);

      ordered.forEach((card) => {
        list.append(card.element);
      });

      cardData.length = 0;
      cardData.push(...ordered);
    };

    /**
     * Select a URL-supplied filter value.
     *
     * When the value does not exist among the generated options, add a
     * temporary option so that the requested filter remains active and the
     * catalogue correctly displays its empty state.
     *
     * @param {HTMLSelectElement} select
     * @param {string} value
     */
    const applySelectFilter = (select, value) => {
      const normalisedValue =
        normaliseCatalogueValue(value);

      const optionExists = Array.from(select.options).some(
        (option) => option.value === normalisedValue,
      );

      if (!optionExists) {
        const option = document.createElement("option");

        option.value = normalisedValue;
        option.textContent = value.trim();
        option.dataset.urlFilterOption = "";

        select.append(option);
      }

      select.value = normalisedValue;
    };

    /**
     * Populate available controls from the current URL.
     */
    const applyInitialFilters = () => {
      const urlParameters = new URLSearchParams(
        window.location.search,
      );

      const search = urlParameters.get(URL_PARAM_SEARCH);
      const category = urlParameters.get(URL_PARAM_CATEGORY);
      const organisation = urlParameters.get(URL_PARAM_ORG);
      const status = urlParameters.get(URL_PARAM_STATUS);

      if (search !== null) {
        searchInput.value = search;
      }

      if (category !== null) {
        applySelectFilter(categorySelect, category);
      }

      if (organisation !== null && organisationSelect) {
        applySelectFilter(organisationSelect, organisation);
      }

      if (status !== null && statusSelect) {
        applySelectFilter(statusSelect, status);
      } else if (status !== null && statusButtons.length) {
        const normalised = normaliseCatalogueValue(status);
        const allowed = new Set(
          statusButtons.map((button) => statusFromButton(button)),
        );

        activeStatus = allowed.has(normalised) ? normalised : "";
        setStatusPressed(activeStatus);
      }
    };

    /**
     * Read the current filter control values.
     *
     * @returns {{
     *   searchTerm: string,
     *   selectedCategory: string,
     *   selectedOrganisation: string,
     *   selectedStatus: string
     * }}
     */
    const readActiveFilters = () => ({
      searchTerm: normaliseCatalogueValue(searchInput.value),
      selectedCategory: normaliseCatalogueValue(
        categorySelect.value,
      ),
      selectedOrganisation: organisationSelect
        ? normaliseCatalogueValue(organisationSelect.value)
        : "",
      selectedStatus: statusSelect
        ? normaliseCatalogueValue(statusSelect.value)
        : statusButtons.length
          ? activeStatus
          : "",
    });

    /**
     * Apply visibility to each card for the active filters.
     *
     * @param {{
     *   searchTerm: string,
     *   selectedCategory: string,
     *   selectedOrganisation: string,
     *   selectedStatus: string
     * }} filters
     * @returns {number}
     */
    const applyCardVisibility = (filters) => {
      let visibleCount = 0;

      cardData.forEach((card) => {
        const matchesSearch =
          filters.searchTerm === "" ||
          card.searchableText.includes(filters.searchTerm);

        const matchesCategory =
          filters.selectedCategory === "" ||
          card.categories.includes(filters.selectedCategory);

        const matchesOrganisation =
          filters.selectedOrganisation === "" ||
          card.organisation === filters.selectedOrganisation;

        const matchesStatus =
          filters.selectedStatus === "" ||
          (filters.selectedStatus === "stable"
            ? card.status === "" || card.status === "stable"
            : card.status === filters.selectedStatus);

        const isVisible =
          matchesSearch &&
          matchesCategory &&
          matchesOrganisation &&
          matchesStatus;

        card.element.hidden = !isVisible;

        if (isVisible) {
          visibleCount += 1;
        }
      });

      return visibleCount;
    };

    /**
     * Update the summary label for the current result set.
     *
     * @param {number} visibleCount
     */
    const updateSummary = (visibleCount) => {
      const totalCount = cardData.length;

      // Keep copy short for the collapsed toolbar (esp. mobile).
      // Page context already implies projects / articles / etc.
      summary.textContent =
        `Showing ${visibleCount} of ${totalCount}`;
    };

    /**
     * Enable or disable the clear button from the active filters.
     *
     * @param {{
     *   searchTerm: string,
     *   selectedCategory: string,
     *   selectedOrganisation: string,
     *   selectedStatus: string
     * }} filters
     */
    const updateClearButton = (filters) => {
      clearButton.disabled =
        filters.searchTerm === "" &&
        filters.selectedCategory === "" &&
        filters.selectedOrganisation === "" &&
        filters.selectedStatus === "";
    };

    /**
     * Show or hide the empty-state element.
     *
     * @param {number} visibleCount
     */
    const updateEmptyState = (visibleCount) => {
      if (emptyState) {
        emptyState.hidden = visibleCount !== 0;
      }
    };

    /**
     * Keep the URL synchronised with the current filters.
     *
     * @param {{
     *   searchTerm: string,
     *   selectedCategory: string,
     *   selectedOrganisation: string,
     *   selectedStatus: string
     * }} filters
     */
    const syncUrlWithFilters = (filters) => {
      const params = new URLSearchParams();

      if (filters.searchTerm) {
        params.set(URL_PARAM_SEARCH, searchInput.value.trim());
      }

      if (filters.selectedCategory) {
        params.set(URL_PARAM_CATEGORY, categorySelect.value);
      }

      if (filters.selectedOrganisation) {
        params.set(URL_PARAM_ORG, organisationSelect.value);
      }

      if (filters.selectedStatus) {
        params.set(
          URL_PARAM_STATUS,
          statusSelect
            ? statusSelect.value
            : filters.selectedStatus,
        );
      }

      if (config.sort && activeSort === SORT_NEWEST) {
        params.set(URL_PARAM_SORT, SORT_NEWEST);
      }

      const url = new URL(window.location.href);

      url.search = params.toString();

      window.history.replaceState(
        window.history.state,
        "",
        `${url.pathname}${url.search}${url.hash}`,
      );
    };

    /**
     * Apply all active catalogue filters.
     */
    const updateCatalogue = () => {
      const filters = readActiveFilters();
      const visibleCount = applyCardVisibility(filters);

      updateSummary(visibleCount);
      updateClearButton(filters);
      updateEmptyState(visibleCount);
      syncUrlWithFilters(filters);
      syncArticlePagerSequence(
        config,
        cardData,
        filters,
        activeSort,
      );
      scheduleCategoryLayout();
    };

    /**
     * Reset all controls and remove filter parameters from the URL.
     */
    const clearFilters = () => {
      searchInput.value = "";
      categorySelect.value = "";
      removeUrlFilterOptions(categorySelect);

      if (organisationSelect) {
        organisationSelect.value = "";
        removeUrlFilterOptions(organisationSelect);
      }

      if (statusSelect) {
        statusSelect.value = "";
        removeUrlFilterOptions(statusSelect);
      }

      if (statusButtons.length) {
        activeStatus = "";
        setStatusPressed("");
      }

      clearCatalogueUrlParameters();
      updateCatalogue();
      searchInput.focus();
    };

    searchInput.addEventListener("input", updateCatalogue);
    categorySelect.addEventListener("change", updateCatalogue);
    clearButton.addEventListener("click", clearFilters);

    if (organisationSelect) {
      organisationSelect.addEventListener(
        "change",
        updateCatalogue,
      );
    }

    if (statusSelect) {
      statusSelect.addEventListener("change", updateCatalogue);
    }

    statusButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const status = statusFromButton(button);

        if (status === activeStatus) {
          return;
        }

        activeStatus = status;
        setStatusPressed(activeStatus);
        updateCatalogue();
      });
    });

    if (config.sort) {
      sortButtons.forEach((button) => {
        button.addEventListener("click", () => {
          const sort = sortFromButton(button);

          if (!sort || sort === activeSort) {
            return;
          }

          activeSort = sort === SORT_NEWEST ? SORT_NEWEST : SORT_ALPHA;
          setSortPressed(activeSort);
          applyCardOrder();
          updateCatalogue();
        });
      });
    }

    /**
     * Category pills set the category filter on this page.
     */
    catalogue
      .querySelectorAll(".catalogue-category")
      .forEach((pill) => {
        if (pill.dataset.categoryFilterBound === "true") {
          return;
        }

        pill.dataset.categoryFilterBound = "true";
        pill.setAttribute(
          "aria-label",
          `Filter by ${pill.textContent?.trim() || "category"}`,
        );

        pill.addEventListener("click", (event) => {
          event.preventDefault();
          event.stopPropagation();

          const label = pill.textContent?.trim() || "";

          if (!label) {
            return;
          }

          applySelectFilter(categorySelect, label);
          revealFilterPanel(filterPanel);
          updateCatalogue();
          categorySelect.focus({ preventScroll: true });
        });
      });

    /**
     * Organisation logos set the organisation filter on this page.
     */
    if (organisationSelect) {
      catalogue
        .querySelectorAll("img.catalogue-logo[data-organisation]")
        .forEach((logo) => {
          if (logo.dataset.organisationFilterBound === "true") {
            return;
          }

          const organisation =
            logo.dataset.organisation?.trim() || "";

          if (!organisation) {
            return;
          }

          logo.dataset.organisationFilterBound = "true";

          let control = logo.closest(
            "[data-organisation-filter-control]",
          );

          if (!control) {
            control = document.createElement("button");
            control.type = "button";
            control.dataset.organisationFilterControl = "";
            logo.replaceWith(control);
            control.append(logo);
          }

          control.setAttribute(
            "aria-label",
            `Filter by ${organisation}`,
          );

          control.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();

            applySelectFilter(organisationSelect, organisation);
            revealFilterPanel(filterPanel);
            updateCatalogue();
            organisationSelect.focus({ preventScroll: true });
          });
        });
    }

    /**
     * Status banners set the status filter on this page.
     */
    if (hasStatusControl) {
      catalogue
        .querySelectorAll(".catalogue-banner[data-banner-status]")
        .forEach((banner) => {
          if (banner.dataset.statusFilterBound === "true") {
            return;
          }

          const status = banner.dataset.bannerStatus?.trim() || "";
          const label = banner.dataset.bannerLabel?.trim() || status;

          if (!status) {
            return;
          }

          banner.dataset.statusFilterBound = "true";
          banner.setAttribute(
            "aria-label",
            `Filter by status ${label}`,
          );

          const activate = (event) => {
            event.preventDefault();
            event.stopPropagation();

            if (statusSelect) {
              applySelectFilter(statusSelect, status);
              revealFilterPanel(filterPanel);
              updateCatalogue();
              statusSelect.focus({ preventScroll: true });
              return;
            }

            const normalised = normaliseCatalogueValue(status);
            const allowed = new Set(
              statusButtons.map((button) => statusFromButton(button)),
            );

            activeStatus = allowed.has(normalised) ? normalised : "";
            setStatusPressed(activeStatus);
            revealFilterPanel(filterPanel);
            updateCatalogue();

            const focusButton = statusButtons.find(
              (button) => statusFromButton(button) === activeStatus,
            );

            focusButton?.focus({ preventScroll: true });
          };

          banner.addEventListener("click", activate);
          banner.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
              activate(event);
            }
          });
        });
    }

    if (config.sort) {
      activeSort = readSortFromUrl();
      setSortPressed(activeSort);
    }

    applyCardOrder();

    applyInitialFilters();
    updateCatalogue();
  }

  const catalogueConfigurations = [
    catalogueConfig({
      id: "project",
      singular: "project",
      plural: "projects",
      organisation: true,
      status: true,
      sort: true,
    }),
    catalogueConfig({
      id: "website",
      singular: "website",
      plural: "websites",
      organisation: true,
      status: true,
      sort: true,
    }),
    catalogueConfig({
      id: "organisation",
      singular: "organisation",
      plural: "organisations",
      sort: true,
    }),
    catalogueConfig({
      id: "policy",
      singular: "policy",
      plural: "policies",
    }),
    catalogueConfig({
      id: "article",
      singular: "article",
      plural: "articles",
      status: true,
      sort: true,
    }),
  ];

  /**
   * Resolve the Projects catalogue path from the current page location.
   *
   * @returns {string}
   */
  function projectsCataloguePath() {
    const path = window.location.pathname;

    if (path.includes("/organisations") || path.includes("/websites")) {
      return "../projects/";
    }

    if (path.includes("/projects")) {
      return "./";
    }

    return "projects/";
  }

  /**
   * Wrap organisation logos in links to the Projects catalogue (org filter).
   *
   * Skipped on the Projects page itself — logos filter in-place there.
   */
  function linkOrganisationLogos() {
    const path = window.location.pathname;

    if (path.includes("/projects") || path.includes("/websites")) {
      return;
    }

    const projectsPath = projectsCataloguePath();

    document
      .querySelectorAll("img.catalogue-logo[data-organisation]")
      .forEach((logo) => {
        const organisation = logo.dataset.organisation?.trim() || "";

        addOrganisationProjectLink(logo, organisation, projectsPath);
      });
  }

  /**
   * On pages without a filter panel, category pills navigate to the Projects
   * catalogue with that category selected.
   */
  function linkStandaloneCategoryPills() {
    const path = window.location.pathname;

    if (
      path.includes("/organisations") ||
      path.includes("/projects") ||
      path.includes("/websites") ||
      path.includes("/policies") ||
      path.includes("/articles")
    ) {
      return;
    }

    document.querySelectorAll(".catalogue-category").forEach((pill) => {
      if (pill.dataset.categoryFilterBound === "true") {
        return;
      }

      const label = pill.textContent?.trim() || "";

      if (!label) {
        return;
      }

      pill.dataset.categoryFilterBound = "true";
      pill.setAttribute("aria-label", `View projects in ${label}`);

      pill.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();

        const url = new URL("projects/", window.location.href);

        url.searchParams.set(URL_PARAM_CATEGORY, label);
        window.location.href = url.href;
      });
    });
  }

  /**
   * On pages without a project status filter, banners navigate to Projects
   * with that status selected. Policies keep banners but have no status
   * control, so do not send those clicks to Projects.
   */
  function linkStandaloneStatusBanners() {
    const path = window.location.pathname;

    if (
      path.includes("/projects") ||
      path.includes("/websites") ||
      path.includes("/policies")
    ) {
      return;
    }

    document
      .querySelectorAll(".catalogue-banner[data-banner-status]")
      .forEach((banner) => {
        if (banner.dataset.statusFilterBound === "true") {
          return;
        }

        const status = banner.dataset.bannerStatus?.trim() || "";
        const label = banner.dataset.bannerLabel?.trim() || status;

        if (!status) {
          return;
        }

        banner.dataset.statusFilterBound = "true";
        banner.setAttribute(
          "aria-label",
          `View ${label} projects`,
        );

        const go = (event) => {
          event.preventDefault();
          event.stopPropagation();

          const url = new URL(
            projectsCataloguePath(),
            window.location.href,
          );

          url.searchParams.set(URL_PARAM_STATUS, status);
          window.location.href = url.href;
        };

        banner.addEventListener("click", go);
        banner.addEventListener("keydown", (event) => {
          if (event.key === "Enter" || event.key === " ") {
            go(event);
          }
        });
      });
  }

  const CATEGORY_ROW_SELECTOR = [
    ".catalogue-grid > ul > li > p:has(> .catalogue-category)",
    ".catalogue-grid > li > p:has(> .catalogue-category)",
  ].join(", ");

  let categoryLayoutFrame = 0;
  let categoryRowObserver = null;
  const categoryRowWidths = new WeakMap();

  /**
   * Coalesce category-row measurements onto the next frame.
   */
  function scheduleCategoryLayout() {
    if (categoryLayoutFrame) {
      return;
    }

    categoryLayoutFrame = requestAnimationFrame(() => {
      categoryLayoutFrame = 0;
      layoutCategoryRows();
    });
  }

  /**
   * @param {HTMLElement} row
   * @returns {HTMLElement[]}
   */
  function categoryPills(row) {
    return Array.from(
      row.querySelectorAll(":scope > .catalogue-category"),
    );
  }

  /**
   * @param {HTMLElement} row
   * @returns {HTMLButtonElement}
   */
  function ensureCategoryMore(row) {
    const existing = row.querySelector(
      ":scope > .catalogue-category-more",
    );

    if (existing instanceof HTMLButtonElement) {
      return existing;
    }

    const more = document.createElement("button");

    more.type = "button";
    more.className = "catalogue-category-more";
    more.hidden = true;
    more.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      row.classList.toggle("is-expanded");
      layoutCategoryRow(row);
    });
    row.append(more);

    return more;
  }

  /**
   * True when every visible pill and the toggle share one line.
   *
   * @param {HTMLElement[]} pills
   * @param {HTMLElement} more
   * @returns {boolean}
   */
  function categoryRowIsOneLine(pills, more) {
    const visible = pills.filter((pill) => !pill.hidden);
    const anchor = visible[0] || more;
    const top = anchor.offsetTop;
    const onLine = (element) => element.offsetTop <= top + 1;

    return visible.every(onLine) && (more.hidden || onLine(more));
  }

  /**
   * Keep one line of pills, with a count for the ones that do not fit.
   *
   * The line's offset moves when pills wrap and then collapse, so each
   * check reads the current first pill instead of a saved position.
   *
   * @param {HTMLElement} row
   */
  function layoutCategoryRow(row) {
    const pills = categoryPills(row);

    if (!pills.length || row.getClientRects().length === 0) {
      return;
    }

    const more = ensureCategoryMore(row);
    const show = (count, toggle) => {
      pills.forEach((pill, index) => {
        pill.hidden = index >= count;
      });
      more.hidden = !toggle;
    };

    if (row.classList.contains("is-expanded")) {
      show(pills.length, false);

      if (categoryRowIsOneLine(pills, more)) {
        row.classList.remove("is-expanded");
        more.hidden = true;
        more.setAttribute("aria-expanded", "false");
        return;
      }

      show(pills.length, true);
      more.textContent = "Less";
      more.setAttribute("aria-expanded", "true");
      more.setAttribute("aria-label", "Show fewer categories");
      return;
    }

    show(pills.length, false);

    if (categoryRowIsOneLine(pills, more)) {
      more.setAttribute("aria-expanded", "false");
      return;
    }

    let count = pills.length;

    while (count > 1) {
      count -= 1;
      show(count, true);
      more.textContent = `+${pills.length - count}`;

      if (categoryRowIsOneLine(pills, more)) {
        break;
      }
    }

    const hiddenCount = pills.length - count;

    more.hidden = false;
    more.textContent = `+${hiddenCount}`;
    more.setAttribute("aria-expanded", "false");
    more.setAttribute(
      "aria-label",
      `Show ${hiddenCount} more categories`,
    );
  }

  /**
   * Measure every visible category row.
   */
  function layoutCategoryRows() {
    document
      .querySelectorAll(CATEGORY_ROW_SELECTOR)
      .forEach((row) => {
        if (row instanceof HTMLElement) {
          layoutCategoryRow(row);
        }
      });
  }

  /**
   * Remeasure when a card's width changes. Height changes from
   * collapsing a row do not count.
   */
  function watchCategoryRows() {
    if (typeof ResizeObserver === "undefined") {
      return;
    }

    if (!categoryRowObserver) {
      categoryRowObserver = new ResizeObserver((entries) => {
        const widthChanged = entries.some((entry) => {
          const width = Math.round(entry.contentRect.width);
          const previous = categoryRowWidths.get(entry.target);

          if (previous === width) {
            return false;
          }

          categoryRowWidths.set(entry.target, width);
          return true;
        });

        if (widthChanged) {
          scheduleCategoryLayout();
        }
      });
    }

    categoryRowObserver.disconnect();
    document
      .querySelectorAll(CATEGORY_ROW_SELECTOR)
      .forEach((row) => {
        categoryRowWidths.delete(row);
        categoryRowObserver.observe(row);
      });
  }

  /**
   * Initialise every catalogue present on the current page.
   */
  function initialiseCatalogues() {
    linkOrganisationLogos();
    catalogueConfigurations.forEach(initialiseCatalogue);
    linkStandaloneCategoryPills();
    linkStandaloneStatusBanners();
    watchCategoryRows();
    scheduleCategoryLayout();

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(() => {
        scheduleCategoryLayout();
      });
    }
  }

  onPageRender(initialiseCatalogues);
})();
