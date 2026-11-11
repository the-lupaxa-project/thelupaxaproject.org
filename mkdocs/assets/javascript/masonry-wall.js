/**
 * Shared masonry wall primitives for Humour.
 * Page scripts supply selectors and optional filter matching.
 */
(() => {
  "use strict";

  const GAP = 16;
  let resizeBound = false;
  let resizeTimer = null;
  const activeMasonries = new Set();

  const shuffle = (nodes) => {
    const arr = Array.from(nodes);
    for (let i = arr.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  };

  const cardTags = (card) =>
    (card.getAttribute("data-tags") || "").split("|").filter(Boolean);

  const normaliseFilter = (value) =>
    String(value ?? "")
      .toLocaleLowerCase("en-GB")
      .replace(/\s+/g, " ")
      .trim();

  /**
   * Pick the filter a shared URL asked for.
   * A known button wins so the address uses its exact value.
   * An unknown value stays selected and matches nothing.
   *
   * @param {NodeListOf<Element> | Element[]} filters
   * @param {string | null} initialFilter
   * @returns {string}
   */
  const resolveSelected = (filters, initialFilter) => {
    if (initialFilter === null || initialFilter === undefined) return "all";
    const wanted = normaliseFilter(initialFilter);
    if (!wanted || wanted === "all") return "all";
    const match = Array.from(filters).find(
      (button) => normaliseFilter(button.getAttribute("data-filter")) === wanted,
    );
    return match ? match.getAttribute("data-filter") : wanted;
  };

  const markActiveFilter = (filters, selected) => {
    const wanted = normaliseFilter(selected);
    filters.forEach((filter) => {
      filter.classList.toggle(
        "is-active",
        normaliseFilter(filter.getAttribute("data-filter")) === wanted,
      );
    });
  };

  const defaultMatchesFilter = (card, selected) =>
    selected === "all" || cardTags(card).includes(selected);

  /**
   * Resolve data-show-count: "all" (default) or a positive integer cap.
   *
   * @param {Element | null} wall
   * @param {number} total
   * @returns {number}
   */
  const resolveShowCount = (wall, total) => {
    if (!wall) return total;
    const raw = String(wall.getAttribute("data-show-count") || "all")
      .trim()
      .toLowerCase();
    if (!raw || raw === "all") return total;
    const limit = Number.parseInt(raw, 10);
    if (!Number.isFinite(limit) || limit < 1) return total;
    return Math.min(limit, total);
  };

  /**
   * Drop tag filter controls that match nothing in the active card set.
   *
   * @param {NodeListOf<Element> | Element[]} filters
   * @param {Element[]} cards
   */
  const pruneUnusedTagFilters = (filters, cards) => {
    const present = new Set();
    cards.forEach((card) => {
      cardTags(card).forEach((tag) => present.add(tag));
    });

    Array.from(filters).forEach((button) => {
      const value = button.getAttribute("data-filter");
      if (
        !value ||
        value === "all" ||
        value === "images" ||
        value === "videos"
      ) {
        return;
      }
      if (present.has(value)) return;

      const previous = button.previousElementSibling;
      if (previous && previous.classList.contains("humour-filter-sep")) {
        previous.remove();
      }
      button.remove();
    });
  };

  const columnCountForWidth = (width) => {
    const cols = Math.floor((width + GAP) / (280 + GAP));
    return Math.max(1, Math.min(cols, 6));
  };

  const layoutMasonry = (masonry, cardSelector) => {
    const cards = Array.from(masonry.querySelectorAll(cardSelector));
    const width = masonry.clientWidth;
    const cols = columnCountForWidth(width);
    const colWidth = cols === 1 ? width : (width - GAP * (cols - 1)) / cols;
    const heights = Array.from({ length: cols }, () => 0);

    masonry.classList.add("is-laid-out");
    masonry.style.height = "";

    cards.forEach((card) => {
      card.style.width = `${colWidth}px`;
      card.style.position = "absolute";
      card.style.left = "0";
      card.style.top = "0";
    });

    cards.forEach((card) => {
      let col = 0;
      for (let i = 1; i < cols; i += 1) {
        if (heights[i] < heights[col]) col = i;
      }
      const x = col * (colWidth + GAP);
      const y = heights[col];
      card.style.transform = `translate(${x}px, ${y}px)`;
      heights[col] += card.offsetHeight + GAP;
    });

    const total = heights.length ? Math.max(...heights) : 0;
    masonry.style.height = `${Math.max(0, total - GAP)}px`;
  };

  const renderMasonry = (masonry, cards, selected, matchesFilter, cardSelector) => {
    cards.forEach((card) => {
      card.style.transform = "";
      card.style.position = "";
      card.style.width = "";
      card.remove();
    });
    cards
      .filter((card) => matchesFilter(card, selected))
      .forEach((card) => masonry.appendChild(card));
    layoutMasonry(masonry, cardSelector);
  };

  const bindResize = () => {
    if (resizeBound) return;
    resizeBound = true;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        activeMasonries.forEach((entry) => {
          if (document.contains(entry.masonry)) {
            layoutMasonry(entry.masonry, entry.cardSelector);
          } else {
            activeMasonries.delete(entry);
          }
        });
      }, 100);
    });
  };

  /**
   * @param {object} options
   * @param {string} options.wallId
   * @param {string} options.masonrySelector
   * @param {string} options.filterSelector
   * @param {string} options.cardSelector
   * @param {(card: Element, selected: string) => boolean} [options.matchesFilter]
   * @param {string | null} [options.initialFilter]
   * @param {(selected: string) => void} [options.onFilter]
   * @returns {{ masonry: Element, wall: Element | null, layout: () => void } | null}
   */
  const init = (options) => {
    const {
      wallId,
      masonrySelector,
      filterSelector,
      cardSelector,
      matchesFilter = defaultMatchesFilter,
      initialFilter = null,
      onFilter,
    } = options;

    const masonry = document.querySelector(masonrySelector);
    const filters = document.querySelectorAll(filterSelector);
    if (!masonry || !filters.length) return null;

    const wall = wallId ? document.getElementById(wallId) : null;
    const nodes = masonry.querySelectorAll(cardSelector);
    const shouldShuffle =
      (wall && wall.getAttribute("data-shuffle") === "true") || false;
    let cards = shouldShuffle ? shuffle(nodes) : Array.from(nodes);

    const showCount = resolveShowCount(wall, cards.length);
    if (showCount < cards.length) {
      if (!shouldShuffle) cards = shuffle(cards);
      cards.slice(showCount).forEach((card) => card.remove());
      cards = cards.slice(0, showCount);
      pruneUnusedTagFilters(filters, cards);
    }

    const activeFilters = document.querySelectorAll(filterSelector);
    let selected = resolveSelected(activeFilters, initialFilter);

    const layout = () => layoutMasonry(masonry, cardSelector);
    const render = (nextSelected) =>
      renderMasonry(masonry, cards, nextSelected, matchesFilter, cardSelector);
    const applyFilter = (nextSelected) => {
      selected = nextSelected || "all";
      markActiveFilter(activeFilters, selected);
      render(selected);
      if (typeof onFilter === "function") onFilter(selected);
    };

    applyFilter(selected);

    activeFilters.forEach((button) => {
      button.addEventListener("click", () => {
        applyFilter(button.getAttribute("data-filter"));
      });
    });

    activeMasonries.forEach((entry) => {
      if (entry.masonry === masonry || !document.contains(entry.masonry)) {
        activeMasonries.delete(entry);
      }
    });
    activeMasonries.add({ masonry, cardSelector });
    bindResize();

    return { masonry, wall, layout };
  };

  window.LupaxaMasonryWall = {
    init,
    cardTags,
    layoutMasonry,
  };
})();
