/**
 * Reputation Engine — SEO QA Validation Logic
 *
 * Three-level quality assurance checks:
 *   1. Article-level  — validates a single published article
 *   2. Domain-level   — validates an entire site
 *   3. Portfolio-level — validates cross-site consistency
 *
 * Designed to run as n8n Code nodes within the SEO QA Agent workflow.
 * Each function returns an array of check results with pass/fail/warn status.
 */

// ─────────────────────────────────────────────────────────────
// Article-Level Checks
// ─────────────────────────────────────────────────────────────

function checkArticle(articleHtml, articleUrl, siteProfile) {
  const results = [];

  // 1. Title tag exists and is reasonable length
  const titleMatch = articleHtml.match(/<title>(.*?)<\/title>/i);
  results.push({
    check_id: "article_title",
    name: "Title tag present",
    status: titleMatch && titleMatch[1].length > 10 && titleMatch[1].length < 70 ? "pass" : "fail",
    detail: titleMatch ? `"${titleMatch[1]}" (${titleMatch[1].length} chars)` : "Missing title tag",
  });

  // 2. Meta description exists
  const descMatch = articleHtml.match(/<meta\s+name="description"\s+content="(.*?)"/i);
  results.push({
    check_id: "article_meta_desc",
    name: "Meta description present",
    status: descMatch && descMatch[1].length > 50 ? "pass" : "fail",
    detail: descMatch ? `${descMatch[1].length} chars` : "Missing meta description",
  });

  // 3. Author byline present
  const hasAuthor = articleHtml.includes("Dr. Sina Bari") || articleHtml.includes("Sina Bari, MD");
  results.push({
    check_id: "article_author",
    name: "Author byline present",
    status: hasAuthor ? "pass" : "fail",
    detail: hasAuthor ? "Author attribution found" : "Missing author byline",
  });

  // 4. Canonical hub link (all sites must link back to sinabarimd.com)
  const hasCanonicalLink = articleHtml.includes("sinabarimd.com");
  results.push({
    check_id: "article_canonical_link",
    name: "Canonical hub link present",
    status: hasCanonicalLink ? "pass" : "fail",
    detail: hasCanonicalLink
      ? "Links to sinabarimd.com found"
      : "Missing required link to sinabarimd.com",
  });

  // 5. Structured data present
  const hasJsonLd = articleHtml.includes("application/ld+json");
  results.push({
    check_id: "article_schema",
    name: "Structured data (JSON-LD) present",
    status: hasJsonLd ? "pass" : "fail",
    detail: hasJsonLd ? "JSON-LD block found" : "Missing structured data",
  });

  // 6. Open Graph tags
  const hasOgTitle = articleHtml.includes('og:title');
  const hasOgDesc = articleHtml.includes('og:description');
  const hasOgType = articleHtml.includes('og:type');
  results.push({
    check_id: "article_og_tags",
    name: "Open Graph meta tags",
    status: hasOgTitle && hasOgDesc && hasOgType ? "pass" : "warn",
    detail: `og:title=${hasOgTitle}, og:description=${hasOgDesc}, og:type=${hasOgType}`,
  });

  // 7. H1 tag present (exactly one)
  const h1Matches = articleHtml.match(/<h1[^>]*>/gi) || [];
  results.push({
    check_id: "article_h1",
    name: "Single H1 tag",
    status: h1Matches.length === 1 ? "pass" : "warn",
    detail: `Found ${h1Matches.length} H1 tag(s)`,
  });

  // 8. Content length check
  const textContent = articleHtml.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
  const wordCount = textContent.split(" ").length;
  const minWords = siteProfile?.content?.default_word_count || 750;
  results.push({
    check_id: "article_word_count",
    name: "Content length",
    status: wordCount >= minWords * 0.8 ? "pass" : "warn",
    detail: `${wordCount} words (minimum: ${minWords})`,
  });

  // 9. No forbidden topics
  const forbidden = siteProfile?.content?.forbidden_topics || [];
  const forbiddenFound = forbidden.filter((topic) =>
    textContent.toLowerCase().includes(topic.toLowerCase())
  );
  results.push({
    check_id: "article_forbidden_topics",
    name: "No forbidden topics",
    status: forbiddenFound.length === 0 ? "pass" : "fail",
    detail:
      forbiddenFound.length === 0
        ? "No forbidden topics detected"
        : `Forbidden topics found: ${forbiddenFound.join(", ")}`,
  });

  // 10. No board certification claims
  const boardCertPatterns = [
    /board.certified/i,
    /board.certification/i,
    /certified by.*board/i,
    /ABPS.certified/i,
  ];
  const hasBoardCertClaim = boardCertPatterns.some((p) => p.test(articleHtml));
  results.push({
    check_id: "article_no_board_cert",
    name: "No board certification claims",
    status: hasBoardCertClaim ? "fail" : "pass",
    detail: hasBoardCertClaim
      ? "CRITICAL: Board certification claim detected — must be removed"
      : "No board certification claims found",
  });

  return results;
}


// ─────────────────────────────────────────────────────────────
// Domain-Level Checks
// ─────────────────────────────────────────────────────────────

function checkDomain(homepageHtml, articlesIndexHtml, siteProfile) {
  const results = [];
  const domain = siteProfile.domain;

  // 1. Homepage has structured data
  const hasSchema = homepageHtml.includes("application/ld+json");
  results.push({
    check_id: "domain_schema",
    name: `${domain} structured data`,
    status: hasSchema ? "pass" : "fail",
    detail: hasSchema ? "Homepage JSON-LD present" : "Missing homepage structured data",
  });

  // 2. Pipeline markers present
  const section = siteProfile.publishing?.pipeline_section;
  if (section) {
    const startMarker = `<!-- PIPELINE:START:${section} -->`;
    const endMarker = `<!-- PIPELINE:END:${section} -->`;
    const hasMarkers = homepageHtml.includes(startMarker) && homepageHtml.includes(endMarker);
    results.push({
      check_id: "domain_pipeline_markers",
      name: `Pipeline markers (${section})`,
      status: hasMarkers ? "pass" : "fail",
      detail: hasMarkers ? "Start and end markers found" : "Missing pipeline markers",
    });
  }

  // 3. Canonical hub link on homepage
  if (domain !== "sinabarimd.com") {
    const linksToHub = homepageHtml.includes("sinabarimd.com");
    results.push({
      check_id: "domain_hub_link",
      name: "Links to canonical hub",
      status: linksToHub ? "pass" : "fail",
      detail: linksToHub ? "sinabarimd.com link found" : "Missing link to sinabarimd.com",
    });
  }

  // 4. Articles index exists and has content
  if (articlesIndexHtml) {
    const articleLinks = (articlesIndexHtml.match(/<a[^>]*href="[^"]*\.html"/gi) || []).length;
    results.push({
      check_id: "domain_articles_index",
      name: "Articles index",
      status: articleLinks > 0 ? "pass" : "warn",
      detail: `${articleLinks} article links found in index`,
    });
  }

  // 5. Robots meta
  const hasRobotsIndex = homepageHtml.includes('robots') && !homepageHtml.includes('noindex');
  results.push({
    check_id: "domain_robots",
    name: "Robots indexing allowed",
    status: hasRobotsIndex ? "pass" : "warn",
    detail: hasRobotsIndex ? "Page is indexable" : "Check robots meta — may be blocking indexing",
  });

  return results;
}


// ─────────────────────────────────────────────────────────────
// Portfolio-Level Checks
// ─────────────────────────────────────────────────────────────

function checkPortfolio(allSiteResults) {
  const results = [];

  // 1. All sites have structured data
  const sitesWithSchema = allSiteResults.filter((s) =>
    s.domainResults.some((r) => r.check_id === "domain_schema" && r.status === "pass")
  );
  results.push({
    check_id: "portfolio_schema_coverage",
    name: "Schema coverage",
    status: sitesWithSchema.length === allSiteResults.length ? "pass" : "warn",
    detail: `${sitesWithSchema.length}/${allSiteResults.length} sites have structured data`,
  });

  // 2. All satellites link to canonical hub
  const satellites = allSiteResults.filter((s) => s.siteId !== "sinabarimd");
  const satellitesLinking = satellites.filter((s) =>
    s.domainResults.some((r) => r.check_id === "domain_hub_link" && r.status === "pass")
  );
  results.push({
    check_id: "portfolio_hub_linking",
    name: "Satellite → hub linking",
    status: satellitesLinking.length === satellites.length ? "pass" : "fail",
    detail: `${satellitesLinking.length}/${satellites.length} satellites link to sinabarimd.com`,
  });

  // 3. No cross-site topic overlap (check for forbidden topic violations)
  const topicViolations = allSiteResults.flatMap((s) =>
    s.articleResults
      .filter((r) => r.check_id === "article_forbidden_topics" && r.status === "fail")
      .map((r) => ({ site: s.siteId, detail: r.detail }))
  );
  results.push({
    check_id: "portfolio_topic_separation",
    name: "Topic separation",
    status: topicViolations.length === 0 ? "pass" : "fail",
    detail:
      topicViolations.length === 0
        ? "No cross-site topic violations"
        : `Violations: ${JSON.stringify(topicViolations)}`,
  });

  // 4. Consistent author attribution
  const authorIssues = allSiteResults.flatMap((s) =>
    s.articleResults
      .filter((r) => r.check_id === "article_author" && r.status === "fail")
      .map((r) => s.siteId)
  );
  results.push({
    check_id: "portfolio_author_consistency",
    name: "Author attribution",
    status: authorIssues.length === 0 ? "pass" : "fail",
    detail:
      authorIssues.length === 0
        ? "All articles have author byline"
        : `Missing author on: ${authorIssues.join(", ")}`,
  });

  // 5. Overall health score
  const allChecks = allSiteResults.flatMap((s) => [
    ...s.domainResults,
    ...s.articleResults,
  ]);
  const passed = allChecks.filter((c) => c.status === "pass").length;
  const total = allChecks.length;
  const score = total > 0 ? Math.round((passed / total) * 100) : 0;
  const grade =
    score >= 95 ? "A+" : score >= 90 ? "A" : score >= 80 ? "B" : score >= 70 ? "C" : "F";

  results.push({
    check_id: "portfolio_health_score",
    name: "Portfolio health",
    status: score >= 90 ? "pass" : score >= 70 ? "warn" : "fail",
    detail: `${grade} (${score}%) — ${passed}/${total} checks passed`,
  });

  return results;
}


// ─────────────────────────────────────────────────────────────
// Exports (for n8n Code node)
// ─────────────────────────────────────────────────────────────

module.exports = { checkArticle, checkDomain, checkPortfolio };
