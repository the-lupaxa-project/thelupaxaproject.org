/**
 * Humour masonry + lightbox. Layout/filter via LupaxaMasonryWall.
 */
(() => {
  "use strict";

  let activeLightbox = null;
  let keydownBound = false;

  const matchesFilter = (card, selected) => {
    if (selected === "all") return true;
    if (selected === "images") return card.getAttribute("data-media") === "image";
    if (selected === "videos") return card.getAttribute("data-media") === "video";
    const tags = window.LupaxaMasonryWall
      ? window.LupaxaMasonryWall.cardTags(card)
      : (card.getAttribute("data-tags") || "").split("|").filter(Boolean);
    return tags.includes(selected);
  };

  const focusableIn = (root) =>
    Array.from(
      root.querySelectorAll(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )
    ).filter((element) => !element.hasAttribute("disabled") && element.offsetParent !== null);

  const initLightbox = (masonry, wall) => {
    const lightbox = document.getElementById("humour-lightbox");
    if (!lightbox) return { open() {}, handleKeydown() {}, destroy() {} };

    const image = lightbox.querySelector(".lightbox-image");
    const video = lightbox.querySelector(".lightbox-video");
    const commentEl = lightbox.querySelector(".lightbox-comment");
    const dateEl = lightbox.querySelector(".lightbox-date");
    const closeBtn = lightbox.querySelector(".lightbox-close");
    const backdrop = lightbox.querySelector(".lightbox-backdrop");
    const prevBtn = lightbox.querySelector(".lightbox-prev");
    const nextBtn = lightbox.querySelector(".lightbox-next");
    let lastFocus = null;
    let currentIndex = -1;

    const visibleOpenButtons = () =>
      Array.from(masonry.querySelectorAll(".humour-card .humour-open"));

    const stopVideo = () => {
      video.pause();
      video.removeAttribute("src");
      video.removeAttribute("poster");
      video.load();
      video.hidden = true;
    };

    const clearImage = () => {
      image.removeAttribute("src");
      image.alt = "";
      image.hidden = true;
    };

    const showFromButton = (button) => {
      const src = button.getAttribute("data-src") || "";
      const type = button.getAttribute("data-type") || "image";
      const poster = button.getAttribute("data-poster") || "";
      const comment = button.getAttribute("data-comment") || "";
      const date = button.getAttribute("data-date") || "";

      stopVideo();
      clearImage();

      if (type === "video") {
        video.src = src;
        if (poster) video.poster = poster;
        video.hidden = false;
        video.currentTime = 0;
        const playPromise = video.play();
        if (playPromise && typeof playPromise.catch === "function") {
          playPromise.catch(() => {});
        }
      } else {
        image.src = src;
        image.alt = comment;
        image.hidden = false;
      }

      commentEl.textContent = comment;
      commentEl.hidden = !comment;
      dateEl.textContent = date;
      dateEl.hidden = !date;
    };

    const reset = () => {
      lightbox.hidden = true;
      document.body.classList.remove("lightbox-open");
      if (wall) wall.inert = false;
      stopVideo();
      clearImage();
      currentIndex = -1;
    };

    const close = () => {
      if (lightbox.hidden) return;
      reset();
      if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
      lastFocus = null;
    };

    const destroy = () => {
      reset();
      lastFocus = null;
    };

    const open = (button) => {
      const buttons = visibleOpenButtons();
      currentIndex = buttons.indexOf(button);
      if (currentIndex < 0) currentIndex = 0;
      lastFocus = button;
      showFromButton(button);
      lightbox.hidden = false;
      document.body.classList.add("lightbox-open");
      if (wall) wall.inert = true;
      closeBtn.focus();
    };

    const step = (delta) => {
      const buttons = visibleOpenButtons();
      if (!buttons.length) return;
      currentIndex = (currentIndex + delta + buttons.length) % buttons.length;
      const button = buttons[currentIndex];
      lastFocus = button;
      showFromButton(button);
    };

    const handleKeydown = (event) => {
      if (lightbox.hidden) return;

      if (event.key === "Escape") {
        event.preventDefault();
        close();
      } else if (event.key === "ArrowRight") {
        event.preventDefault();
        step(1);
      } else if (event.key === "ArrowLeft") {
        event.preventDefault();
        step(-1);
      } else if (event.key === "Tab") {
        const focusables = focusableIn(lightbox);
        if (!focusables.length) {
          event.preventDefault();
          return;
        }
        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    };

    closeBtn.addEventListener("click", close);
    backdrop.addEventListener("click", close);
    prevBtn.addEventListener("click", () => step(-1));
    nextBtn.addEventListener("click", () => step(1));

    return { open, handleKeydown, destroy };
  };

  const cleanupActiveLightbox = () => {
    if (activeLightbox) activeLightbox.destroy();
    activeLightbox = null;
  };

  const CATEGORY_PARAM = "category";

  const categoryFromUrl = () =>
    new URLSearchParams(window.location.search).get(CATEGORY_PARAM);

  const syncCategoryUrl = (selected) => {
    const url = new URL(window.location.href);
    const params = new URLSearchParams(url.search);

    if (!selected || selected === "all") {
      params.delete(CATEGORY_PARAM);
    } else {
      params.set(CATEGORY_PARAM, selected);
    }

    const search = params.toString();
    const next = `${url.pathname}${search ? `?${search}` : ""}${url.hash}`;
    const current = `${window.location.pathname}${window.location.search}${window.location.hash}`;
    if (next === current) return;

    window.history.replaceState(window.history.state, "", next);
  };

  const initHumourWall = () => {
    cleanupActiveLightbox();
    const wallApi = window.LupaxaMasonryWall;
    if (!wallApi) return;

    const result = wallApi.init({
      wallId: "humour-wall",
      masonrySelector: ".humour-masonry",
      filterSelector: ".humour-filter",
      cardSelector: ".humour-card",
      matchesFilter,
      initialFilter: categoryFromUrl(),
      onFilter: syncCategoryUrl,
    });
    if (!result) return;

    const { masonry, wall, layout } = result;
    activeLightbox = initLightbox(masonry, wall);

    masonry.addEventListener("click", (event) => {
      const openButton = event.target.closest(".humour-open");
      if (!openButton || !masonry.contains(openButton)) return;
      activeLightbox.open(openButton);
    });

    masonry.querySelectorAll(".humour-image").forEach((media) => {
      const relayout = () => layout();
      if (media.tagName === "VIDEO") {
        media.addEventListener("loadedmetadata", relayout);
        media.addEventListener("error", relayout);
      } else if (!media.complete) {
        media.addEventListener("load", relayout);
        media.addEventListener("error", relayout);
      }
    });

    if (!keydownBound) {
      keydownBound = true;
      document.addEventListener("keydown", (event) => {
        if (activeLightbox) activeLightbox.handleKeydown(event);
      });
    }
  };

  const lifecycle = window.LupaxaPageLifecycle;
  if (lifecycle && lifecycle.onPageRender) {
    lifecycle.onPageRender(initHumourWall);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initHumourWall);
  } else {
    initHumourWall();
  }
})();
