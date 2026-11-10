---
hide:
  - navigation
  - toc
banner_expiry_days: 28
---

{{ filter_panel(
    "website",
    search_label="Search websites",
    search_placeholder="Search by website name, description, or category...",
    summary_text="Showing…",
    include_organisation=True,
    include_status=True,
    include_sort=True,
) }}

{{ catalogue_grid("website", "website", banner_expiry_days=page.meta.banner_expiry_days or 28) }}

{{ catalogue_empty(
    "website",
    "No matching websites",
    "Try changing the search text or selecting different filters.",
) }}
