---
hide:
  - navigation
  - toc
---

<div class="filter-panel filter-panel--with-sort" data-article-filters data-banner-expiry-days="28" markdown="0">

    <div class="filter-panel-toolbar">
        <button
            type="button"
            class="md-button lupaxa-button filter-panel-expand"
            data-filter-expand
            aria-expanded="false"
        >
            <span class="filter-panel-expand__icon filter-panel-expand__icon--show" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" focusable="false">
                <path d="M6 13h12v-2H6m-3-5v2h18V6M10 18h4v-2h-4v2Z"/>
            </svg>
        </span>
        <span class="filter-panel-expand__icon filter-panel-expand__icon--hide" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" focusable="false">
                <path d="M14.76 20.83 17.6 18l-2.84-2.83 1.41-1.41L19 16.57l2.83-2.81 1.41 1.41L20.41 18l2.83 2.83-1.41 1.41L19 19.41l-2.83 2.83-1.41-1.41M6 13h7.07c.14-.71.4-1.38.76-2H6m-3-5v2h18V6H3Z"/>
            </svg>
        </span>
            <span class="filter-panel-expand__label">Show Filters</span>
        </button>
        <div
            class="filter-panel-summary"
            aria-live="polite"
            data-article-summary
        >
            Showing…
        </div>
    </div>
  <div class="filter-panel-search">
    <label for="article-search">Search articles</label>
    <input
      id="article-search"
      type="search"
      placeholder="Search by title, description, or tag"
      autocomplete="off"
      data-article-search
    />
  </div>
  <div class="filter-panel-select">
    <label for="article-category">Tag</label>
    <select id="article-category" data-article-category>
      <option value="">All Tags</option>
    </select>
  </div>
  <div class="filter-panel-toggle" role="group" aria-labelledby="article-status-label">
    <label id="article-status-label">View Articles</label>
    <div class="filter-panel-toggle__options">
      <button
        type="button"
        class="filter-panel-toggle__option"
        data-article-status="all"
        aria-pressed="true"
      >
        All
      </button>
      <button
        type="button"
        class="filter-panel-toggle__option"
        data-article-status="new"
        aria-pressed="false"
      >
        New
      </button>
    </div>
  </div>
  <div class="filter-panel-toggle" role="group" aria-labelledby="article-sort-label">
    <label id="article-sort-label">Sort</label>
    <div class="filter-panel-toggle__options">
      <button
        type="button"
        class="filter-panel-toggle__option"
        data-article-sort="alpha"
        aria-pressed="true"
      >
        A–Z
      </button>
      <button
        type="button"
        class="filter-panel-toggle__option"
        data-article-sort="newest"
        aria-pressed="false"
      >
        Newest
      </button>
    </div>
  </div>
  <div class="filter-panel-actions">
    <button
      type="button"
      class="md-button lupaxa-button filter-panel-clear"
      data-article-clear
    >
      Clear filters
    </button>
  </div>
</div>

<div class="grid cards catalogue-grid catalogue-grid--articles" data-article-catalogue markdown>

-   **[Certificates Without the Jargon](articles/certificates-without-the-jargon.md)**

    ![Article](assets/images/articles/certificates-without-the-jargon.webp){ class="catalogue-logo" data-name="Certificates Without the Jargon" data-publish-date="2026-07-30T16:03:17" }

    X.509 certificates in plain language. Keys, CSRs, self-signed versus CA-
    signed, trust stores, and what actually matters when you generate certs
    for tools and tests.

    <span class="catalogue-category">Certificates</span>
    <span class="catalogue-category">Security</span>
    <span class="catalogue-category">Tools</span>

-   **[CLI Design](articles/cli-design.md)**

    ![Article](assets/images/articles/cli-design.webp){ class="catalogue-logo" data-name="CLI Design" data-publish-date="2026-07-30T14:04:44" }

    Practical CLI design for open-source tools. Flags and arguments, exit
    codes, stdout versus stderr, helpful errors, and interfaces that feel
    good in scripts and in human hands.

    <span class="catalogue-category">CLI</span>
    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Tools</span>

-   **[Coding Standards](articles/coding-standards.md)**

    ![Article](assets/images/articles/coding-standards.webp){ class="catalogue-logo" data-name="Coding Standards" data-publish-date="2026-07-30T10:47:40" }

    What coding standards actually cover, why they save review time, and how
    to enforce them with linters, formatters, CI checks, editor settings,
    and hooks instead of nagging.

    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Standards</span>

-   **[Config Design](articles/config-design.md)**

    ![Article](assets/images/articles/config-design.webp){ class="catalogue-logo" data-name="Config Design" data-publish-date="2026-07-30T16:03:17" }

    Practical configuration design for tools. Flags, environment variables,
    files, precedence, secrets, and defaults that stay understandable as
    projects grow.

    <span class="catalogue-category">Configuration</span>
    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Tools</span>

-   **[Containers for CLI Tools](articles/containers-for-cli-tools.md)**

    ![Article](assets/images/articles/containers-for-cli-tools.webp){ class="catalogue-logo" data-name="Containers for CLI Tools" data-publish-date="2026-07-30T16:03:17" }

    When and how to ship a CLI tool as a container. Pinning base images,
    running as non-root, keeping the attack surface small, and avoiding
    container anti-patterns for simple utilities.

    <span class="catalogue-category">Containers</span>
    <span class="catalogue-category">Security</span>
    <span class="catalogue-category">Tools</span>

-   **[Contributing Without the Drama](articles/contributing-without-the-drama.md)**

    ![Article](assets/images/articles/contributing-without-the-drama.webp){ class="catalogue-logo" data-name="Contributing Without the Drama" data-publish-date="2026-07-30T14:04:44" }

    How to open issues and pull requests people actually want to merge.
    Small diffs, clear context, real reproduction steps, and knowing when an
    argument is not worth having.

    <span class="catalogue-category">Community</span>
    <span class="catalogue-category">Contributing</span>
    <span class="catalogue-category">Open Source</span>

-   **[Cybersecurity & Chess](articles/cybersecurity-and-chess.md)**

    ![Article](assets/images/articles/cybersecurity-and-chess.webp){ class="catalogue-logo" data-name="Cybersecurity &amp; Chess" data-publish-date="2026-07-30T10:47:40" }

    The strategic parallels between cybersecurity and chess. Reading your
    opponent, adapting when the board changes, keeping tactics in service of
    strategy, and taking risks you have actually priced.

    <span class="catalogue-category">Security</span>
    <span class="catalogue-category">Strategy</span>

-   **[Dependency Hygiene](articles/dependency-hygiene.md)**

    ![Article](assets/images/articles/dependency-hygiene.webp){ class="catalogue-logo" data-name="Dependency Hygiene" data-publish-date="2026-07-30T14:04:44" }

    Practical dependency hygiene for small teams and open-source projects.
    Pinning, lockfiles, audits, supply-chain basics, and keeping your supply
    line trustworthy without enterprise ceremony.

    <span class="catalogue-category">Dependencies</span>
    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Security</span>

-   **[Deprecation Without Chaos](articles/deprecation-without-chaos.md)**

    ![Article](assets/images/articles/deprecation-without-chaos.webp){ class="catalogue-logo" data-name="Deprecation Without Chaos" data-publish-date="2026-07-30T16:03:17" }

    How to retire APIs and flags without ambushing anyone. Warnings people
    actually see, version gates they can plan around, cheap migrations, and
    removals that happen on purpose.

    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Open Source</span>
    <span class="catalogue-category">Process</span>

-   **[Docs That Don't Rot](articles/docs-that-dont-rot.md)**

    ![Article](assets/images/articles/docs-that-dont-rot.webp){ class="catalogue-logo" data-name="Docs That Don&#x27;t Rot" data-publish-date="2026-07-30T14:04:44" }

    How to keep project documentation alive. Examples as tests, docs sites
    that ship with releases, screenshots that stay honest, and habits that
    stop docs from quietly lying.

    <span class="catalogue-category">Documentation</span>
    <span class="catalogue-category">Open Source</span>

-   **[Encryption at Rest for Repos](articles/encryption-at-rest-for-repos.md)**

    ![Article](assets/images/articles/encryption-at-rest-for-repos.webp){ class="catalogue-logo" data-name="Encryption at Rest for Repos" data-publish-date="2026-07-30T16:03:17" }

    Encrypting secrets inside Git repositories. When git-crypt and similar
    tools help, where key management goes wrong, and safer patterns for
    small teams.

    <span class="catalogue-category">Encryption</span>
    <span class="catalogue-category">Git</span>
    <span class="catalogue-category">Security</span>

-   **[Error Handling People Can Use](articles/error-handling-people-can-use.md)**

    ![Article](assets/images/articles/error-handling-people-can-use.webp){ class="catalogue-logo" data-name="Error Handling People Can Use" data-publish-date="2026-07-30T16:03:17" }

    Practical error handling for CLIs and libraries. Clear messages, exit
    codes, retries, typed failures, and when to crash versus recover.

    <span class="catalogue-category">CLI</span>
    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Tools</span>

-   **[Git Workflows for Tiny Teams](articles/git-workflows-for-tiny-teams.md)**

    ![Article](assets/images/articles/git-workflows-for-tiny-teams.webp){ class="catalogue-logo" data-name="Git Workflows for Tiny Teams" data-publish-date="2026-07-30T16:03:17" }

    Practical Git workflows for small teams and solo maintainers. Trunk-
    based development, short-lived branches, pull requests, and release tags
    without enterprise branching theatre.

    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Git</span>
    <span class="catalogue-category">Process</span>

-   **[GitHub Actions](articles/github-actions.md)**

    ![Article](assets/images/articles/github-actions.webp){ class="catalogue-logo" data-name="GitHub Actions" data-publish-date="2026-07-30T10:47:40" }

    Build a working CI/CD pipeline with GitHub Actions, from a first build-
    and-test workflow to deploying an artefact, with the YAML to copy and
    the habits that keep workflows fast and safe.

    <span class="catalogue-category">CI/CD</span>
    <span class="catalogue-category">GitHub</span>

-   **[Input Validation That Sticks](articles/input-validation-that-sticks.md)**

    ![Article](assets/images/articles/input-validation-that-sticks.webp){ class="catalogue-logo" data-name="Input Validation That Sticks" data-publish-date="2026-07-30T16:03:17" }

    Practical input validation for CLIs and small services. Paths, URLs,
    subprocesses, sizes, and the failure modes that let an attacker steer
    your tool.

    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Security</span>

-   **[Key Lifecycle](articles/key-lifecycle.md)**

    ![Article](assets/images/articles/key-lifecycle.webp){ class="catalogue-logo" data-name="Key Lifecycle" data-publish-date="2026-07-30T16:03:17" }

    The key lifecycle for small security tools. Generate, distribute,
    rotate, revoke, and retire cryptographic keys and certificates without
    drama.

    <span class="catalogue-category">Encryption</span>
    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Security</span>

-   **[Least Privilege for CI](articles/least-privilege-for-ci.md)**

    ![Article](assets/images/articles/least-privilege-for-ci.webp){ class="catalogue-logo" data-name="Least Privilege for CI" data-publish-date="2026-07-30T16:03:17" }

    Hardening CI/CD credentials. Short-lived tokens, OIDC, protected
    environments, and the GitHub Actions patterns that keep long-lived
    secrets out of your pipelines.

    <span class="catalogue-category">CI/CD</span>
    <span class="catalogue-category">Security</span>

-   **[Licenses for Humans](articles/licenses-for-humans.md)**

    ![Article](assets/images/articles/licenses-for-humans.webp){ class="catalogue-logo" data-name="Licenses for Humans" data-publish-date="2026-07-30T14:04:44" }

    A plain-language guide to open-source licenses for people publishing
    tools. MIT, Apache-2.0, and the GPL family, what each one asks of your
    users, and how to choose without a law degree.

    <span class="catalogue-category">Community</span>
    <span class="catalogue-category">Licenses</span>
    <span class="catalogue-category">Open Source</span>

-   **[Maintainer Boundaries](articles/maintainer-boundaries.md)**

    ![Article](assets/images/articles/maintainer-boundaries.webp){ class="catalogue-logo" data-name="Maintainer Boundaries" data-publish-date="2026-07-30T16:03:17" }

    How open-source maintainers stay in the game. Write down scope, decline
    without writing an essay, publish honest support expectations, and
    protect review time before it runs out.

    <span class="catalogue-category">Community</span>
    <span class="catalogue-category">Maintainers</span>
    <span class="catalogue-category">Open Source</span>

-   **[mTLS and Client Certificates](articles/mtls-and-client-certificates.md)**

    ![Article](assets/images/articles/mtls-and-client-certificates.webp){ class="catalogue-logo" data-name="mTLS and Client Certificates" data-publish-date="2026-07-30T16:03:17" }

    Mutual TLS and client certificates in practice. How they differ from
    ordinary HTTPS, when they are worth the trouble, and how small tools
    should issue and verify them.

    <span class="catalogue-category">Certificates</span>
    <span class="catalogue-category">Security</span>

-   **[Observability for Small Projects](articles/observability-for-small-projects.md)**

    ![Article](assets/images/articles/observability-for-small-projects.webp){ class="catalogue-logo" data-name="Observability for Small Projects" data-publish-date="2026-07-30T14:04:44" }

    Practical observability for CLIs, libraries, and small services. Useful
    logs, health signals, failure modes, and knowing what broke without
    needing an enterprise APM stack.

    <span class="catalogue-category">DevOps</span>
    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Observability</span>

-   **[Practical SECURITY.md](articles/practical-security-md.md)**

    ![Article](assets/images/articles/practical-security-md.webp){ class="catalogue-logo" data-name="Practical SECURITY.md" data-publish-date="2026-07-31T17:42:00" }

    A practical SECURITY.md playbook for small projects. What to include,
    example structure, scope statements, and making the security policy easy
    to find and follow.

    <span class="catalogue-category">Documentation</span>
    <span class="catalogue-category">Open Source</span>
    <span class="catalogue-category">Security</span>

-   **[Programming Fundamentals](articles/programming-fundamentals.md)**

    ![Article](assets/images/articles/programming-fundamentals.webp){ class="catalogue-logo" data-name="Programming Fundamentals" data-publish-date="2026-07-30T10:47:40" }

    Why the principles underneath programming outlast any single language,
    and how a grip on algorithms, data structures, and design makes picking
    up new syntax the easy part.

    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Fundamentals</span>

-   **[README as Product](articles/readme-as-product.md)**

    ![Article](assets/images/articles/readme-as-product.webp){ class="catalogue-logo" data-name="README as Product" data-publish-date="2026-07-30T14:04:44" }

    Your README is the product page for an open-source project. Install
    steps that work, examples that ran, badges that tell the truth, and the
    shortest path from curiosity to a first success.

    <span class="catalogue-category">Documentation</span>
    <span class="catalogue-category">Open Source</span>

-   **[Red Team vs Blue Team](articles/red-team-vs-blue-team.md)**

    ![Article](assets/images/articles/red-team-vs-blue-team.webp){ class="catalogue-logo" data-name="Red Team vs Blue Team" data-publish-date="2026-07-30T10:47:40" }

    What Red Teams and Blue Teams actually do, why running them against each
    other finds the weaknesses a questionnaire never will, and where Purple,
    Green, and White Teams fit around them.

    <span class="catalogue-category">Ops</span>
    <span class="catalogue-category">Security</span>

-   **[Release Automation](articles/release-automation.md)**

    ![Article](assets/images/articles/release-automation.webp){ class="catalogue-logo" data-name="Release Automation" data-publish-date="2026-07-30T14:04:44" }

    How to make releases boring. Tags as the source of truth, changelogs
    people can read, scoped publishing tokens, and CI guardrails that stop a
    bad release before it reaches a registry.

    <span class="catalogue-category">Automation</span>
    <span class="catalogue-category">CI/CD</span>
    <span class="catalogue-category">Open Source</span>

-   **[Reproducible Builds](articles/reproducible-builds.md)**

    ![Article](assets/images/articles/reproducible-builds.webp){ class="catalogue-logo" data-name="Reproducible Builds" data-publish-date="2026-07-30T16:03:17" }

    Lightweight reproducible builds for small tools. Pinning inputs, killing
    nondeterminism, and getting to bit-for-bit or near-identical releases
    without enterprise ceremony.

    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Security</span>

-   **[Responsible Dependency Updates](articles/responsible-dependency-updates.md)**

    ![Article](assets/images/articles/responsible-dependency-updates.webp){ class="catalogue-logo" data-name="Responsible Dependency Updates" data-publish-date="2026-07-30T16:03:17" }

    A practical cadence for dependency updates. Dependabot-style PRs, ignore
    rules, reading majors, and keeping upgrades boring without ignoring
    security fixes.

    <span class="catalogue-category">Dependencies</span>
    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Security</span>

-   **[Right Tools for the Job](articles/right-tools-for-the-job.md)**

    ![Article](assets/images/articles/right-tools-for-the-job.webp){ class="catalogue-logo" data-name="Right Tools for the Job" data-publish-date="2026-07-30T16:03:17" }

    How to match languages, operating systems, cloud providers, frameworks,
    and databases to what a project actually needs, instead of forcing one
    familiar stack onto every problem.

    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Tools</span>

-   **[SAST and DAST](articles/sast-and-dast.md)**

    ![Article](assets/images/articles/sast-and-dast.webp){ class="catalogue-logo" data-name="SAST and DAST" data-publish-date="2026-07-30T16:03:17" }

    What static and dynamic application security testing each catch, why
    they find different bugs, and how to run SAST in CI and DAST against a
    deployed environment without drowning the team in findings.

    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Security</span>
    <span class="catalogue-category">Testing</span>

-   **[Secrets Management](articles/secrets-management.md)**

    ![Article](assets/images/articles/secrets-management.webp){ class="catalogue-logo" data-name="Secrets Management" data-publish-date="2026-07-30T10:47:40" }

    What counts as a secret, the five ways secrets management usually goes
    wrong, and the practices and tools that keep credentials out of your
    codebase and under control.

    <span class="catalogue-category">DevOps</span>
    <span class="catalogue-category">Security</span>

-   **[Secure Defaults](articles/secure-defaults.md)**

    ![Article](assets/images/articles/secure-defaults.webp){ class="catalogue-logo" data-name="Secure Defaults" data-publish-date="2026-07-30T16:03:17" }

    Designing secure defaults for tools and libraries. Fail closed, least
    privilege, dangerous features opt-in, and interfaces that make the safe
    path the easy path.

    <span class="catalogue-category">Design</span>
    <span class="catalogue-category">Security</span>

-   **[Secure Logging](articles/secure-logging.md)**

    ![Article](assets/images/articles/secure-logging.webp){ class="catalogue-logo" data-name="Secure Logging" data-publish-date="2026-07-30T16:03:17" }

    Practical secure logging for tools and services. What never to log,
    redaction, crash reports, debug flags, and keeping observability from
    becoming a leak.

    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Security</span>

-   **[Security by Design](articles/security-by-design.md)**

    ![Article](assets/images/articles/security-by-design.webp){ class="catalogue-logo" data-name="Security by Design" data-publish-date="2026-07-30T10:47:40" }

    Security by Design in practice. The principles behind it, why fixing
    flaws at design time is cheaper, and what it looks like applied to
    software, infrastructure, and cloud environments.

    <span class="catalogue-category">Design</span>
    <span class="catalogue-category">Security</span>

-   **[Security Disclosures That Work](articles/security-disclosures-that-work.md)**

    ![Article](assets/images/articles/security-disclosures-that-work.webp){ class="catalogue-logo" data-name="Security Disclosures That Work" data-publish-date="2026-07-30T16:03:17" }

    Practical security disclosure for small open-source projects.
    SECURITY.md, private reporting, triage, credit, and promises maintainers
    can actually keep.

    <span class="catalogue-category">Open Source</span>
    <span class="catalogue-category">Security</span>
    <span class="catalogue-category">Vulnerability Reporting</span>

-   **[Semantic Versioning](articles/semantic-versioning.md)**

    ![Article](assets/images/articles/semantic-versioning.webp){ class="catalogue-logo" data-name="Semantic Versioning" data-publish-date="2026-07-30T14:04:44" }

    Semantic versioning as it actually plays out in open-source tools. What
    counts as breaking, how to live in 0.x honestly, why changelogs are part
    of the version number, and how to keep upgrades boring.

    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Open Source</span>
    <span class="catalogue-category">Standards</span>

-   **[Supply-Chain Signing](articles/supply-chain-signing.md)**

    ![Article](assets/images/articles/supply-chain-signing.webp){ class="catalogue-logo" data-name="Supply-Chain Signing" data-publish-date="2026-07-30T16:03:17" }

    Practical supply-chain signing for open-source releases. Checksums,
    signatures, provenance, and verification steps users can actually
    follow.

    <span class="catalogue-category">Open Source</span>
    <span class="catalogue-category">Security</span>

-   **[Testing What Matters](articles/testing-what-matters.md)**

    ![Article](assets/images/articles/testing-what-matters.webp){ class="catalogue-logo" data-name="Testing What Matters" data-publish-date="2026-07-30T14:04:44" }

    Why high coverage can be a vanity metric, how to test behaviour instead
    of mocks, and how small open-source projects can build a test suite that
    catches real regressions without drowning contributors.

    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Testing</span>

-   **[The Cybersecurity Rainbow](articles/the-cybersecurity-rainbow.md)**

    ![Article](assets/images/articles/the-cybersecurity-rainbow.webp){ class="catalogue-logo" data-name="The Cybersecurity Rainbow" data-publish-date="2026-07-30T10:47:40" }

    A map of the colour-coded cybersecurity teams. Red, Blue, Purple, Green,
    Yellow, Orange, and White, what each one is responsible for, and how
    they fit together into one security programme.

    <span class="catalogue-category">Ops</span>
    <span class="catalogue-category">Security</span>

-   **[The Optimisation Trap](articles/the-optimization-trap.md)**

    ![Article](assets/images/articles/the-optimization-trap.webp){ class="catalogue-logo" data-name="The Optimisation Trap" data-publish-date="2026-07-30T10:47:40" }

    Why capable engineers waste time polishing things that should not exist,
    how to tell warranted optimisation from busywork, and how first
    principles thinking keeps improvements pointed at something that
    matters.

    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Mindset</span>

-   **[Threat Modelling for Small Tools](articles/threat-modelling-for-small-tools.md)**

    ![Article](assets/images/articles/threat-modelling-for-small-tools.webp){ class="catalogue-logo" data-name="Threat Modelling for Small Tools" data-publish-date="2026-07-30T16:03:17" }

    Lightweight threat modelling for CLIs, libraries, and small services.
    Assets, attackers, trust boundaries, and a practical checklist without
    enterprise ceremony.

    <span class="catalogue-category">Design</span>
    <span class="catalogue-category">Engineering</span>
    <span class="catalogue-category">Security</span>

-   **[Understanding CI/CD](articles/understanding-ci-cd.md)**

    ![Article](assets/images/articles/understanding-ci-cd.webp){ class="catalogue-logo" data-name="Understanding CI/CD" data-publish-date="2026-07-30T10:47:40" }

    What continuous integration and continuous delivery buy you, what they
    cost, and the concrete guardrails (feature flags, staging, monitoring,
    canaries, rollbacks) that make automatic deployment survivable.

    <span class="catalogue-category">CI/CD</span>
    <span class="catalogue-category">DevOps</span>

</div>

<div class="catalogue-empty-state" data-article-empty hidden markdown>

:material-magnify: No articles match the current filters.

Try clearing the search or choosing a different tag or status.

</div>
