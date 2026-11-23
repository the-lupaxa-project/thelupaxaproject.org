---
hide:
  - navigation
  - toc
---

{% set wall = humour_data() %}

<div
  id="humour-wall"
  data-shuffle="{{ 'true' if wall.page.get('shuffle', false) else 'false' }}"
  data-show-count="{{ wall.page.get('show_count', 'all') | e }}"
>
  <nav class="humour-filters" aria-label="Filter humour by tag">
    <button type="button" class="humour-filter is-active" data-filter="all" aria-pressed="true">All</button>
    {% for tag in humour_wall_tags() %}
    <span class="humour-filter-sep" aria-hidden="true">·</span>
    <button type="button" class="humour-filter" data-filter="{{ tag | e }}" aria-pressed="false">{{ tag | e }}</button>
    {% endfor %}
  </nav>
  {% if wall.page.get('show_media_filters', false) %}
  <nav class="humour-filters humour-filters-media" aria-label="Filter by media type">
    <button type="button" class="humour-filter" data-filter="images" aria-pressed="false">images</button>
    <span class="humour-filter-sep" aria-hidden="true">·</span>
    <button type="button" class="humour-filter" data-filter="videos" aria-pressed="false">videos</button>
  </nav>
  {% endif %}

  <div class="humour-masonry">
    {% for item in wall_humour_entries() %}
    {% set is_video = item.get('video') %}
    {% set media_src = item.video if is_video else item.image %}
    {% set media_url = media_src if humour_media_is_remote(media_src) else media_src | relative_url %}
    {% set poster_raw = item.get('poster', '') %}
    {% set poster_url = poster_raw if (not poster_raw or humour_media_is_remote(poster_raw)) else poster_raw | relative_url %}
    {% set media_tag = 'videos' if is_video else 'images' %}
    {% set item_tags = [media_tag] + (item.get('tags') or []) %}
    {% set media_id = humour_media_id(media_src) %}
    <article class="humour-card{% if is_video %} is-video{% endif %}" data-tags="{{ item_tags | join('|') | e }}" data-media="{{ 'video' if is_video else 'image' }}" style="{% set card_bg = item.get('card_color') or wall.page.get('card_color') %}{% set card_fg = item.get('text_color') or wall.page.get('card_text_color') or wall.page.get('text_color') %}{% if card_bg %}background: {{ card_bg | e }}; {% endif %}{% if card_fg %}color: {{ card_fg | e }};{% endif %}">
      <button type="button" class="humour-open" data-id="{{ media_id | e }}" data-type="{{ 'video' if is_video else 'image' }}" data-src="{{ media_url | e }}" data-poster="{{ poster_url | e }}" data-comment="{{ item.get('comment', '') | e }}" data-date="{{ item.get('date', '') | e }}" aria-label="Open {% if is_video %}video{% else %}image{% endif %}{% if item.get('comment') %}: {{ item.comment | e }}{% endif %}">
        <span class="humour-media">
          {% if is_video %}
          <video class="humour-image humour-video" src="{{ media_url | e }}" {% if poster_url %}poster="{{ poster_url | e }}"{% endif %} muted playsinline preload="metadata" {% if item.get('width') %}width="{{ item.width | int }}"{% endif %} {% if item.get('height') %}height="{{ item.height | int }}"{% endif %} {% if item.get('width') and item.get('height') %}style="aspect-ratio: {{ item.width | int }} / {{ item.height | int }};"{% elif item.get('aspect_ratio') %}style="aspect-ratio: {{ item.aspect_ratio | e }};"{% endif %}></video>
          <span class="humour-play" aria-hidden="true">▶</span>
          {% else %}
          <img class="humour-image" src="{{ media_url | e }}" alt="{{ item.get('comment', '') | e }}" loading="lazy" decoding="async" {% if item.get('width') %}width="{{ item.width | int }}"{% endif %} {% if item.get('height') %}height="{{ item.height | int }}"{% endif %} {% if item.get('width') and item.get('height') %}style="aspect-ratio: {{ item.width | int }} / {{ item.height | int }};"{% elif item.get('aspect_ratio') %}style="aspect-ratio: {{ item.aspect_ratio | e }};"{% endif %} />
          {% endif %}
        </span>
      </button>
      {% if item.get('comment') or item.get('date') %}
      <div class="humour-meta">
        {% if item.get('comment') %}
        <p class="humour-comment">{{ item.comment | e }}</p>
        {% endif %}
        {% if item.get('date') %}
        <div class="humour-date">{{ item.date | e }}</div>
        {% endif %}
      </div>
      {% endif %}
    </article>
    {% endfor %}
  </div>
</div>

<div
  id="humour-lightbox"
  class="humour-lightbox"
  hidden
  role="dialog"
  aria-modal="true"
  aria-label="Media viewer"
>
  <button type="button" class="lightbox-backdrop" aria-label="Close"></button>
  <button type="button" class="lightbox-prev" aria-label="Previous">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M15.41 7.41 14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
    </svg>
  </button>
  <div class="lightbox-dialog">
    <button type="button" class="lightbox-print" aria-label="Print">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z"/>
      </svg>
    </button>
    <button type="button" class="lightbox-close" aria-label="Close">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
      </svg>
    </button>
    <div class="lightbox-panel">
      <img class="lightbox-image" src="" alt="" hidden />
      <video class="lightbox-video" controls playsinline hidden></video>
      <p class="lightbox-comment" hidden></p>
      <div class="lightbox-date" hidden></div>
    </div>
  </div>
  <button type="button" class="lightbox-next" aria-label="Next">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M10 6 8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
    </svg>
  </button>
</div>
