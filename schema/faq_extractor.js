/**
 * FAQ Schema Extractor
 *
 * Scans article HTML for Q&A patterns and generates FAQPage
 * structured data. Used by the Content Publisher to auto-generate
 * FAQ schema from article content.
 *
 * Pattern: <h3>Question text?</h3> followed by <p>Answer text</p>
 */

function extractFaqSchema(contentHtml, articleUrl) {
  // Match <h3>Question?</h3> followed by <p>Answer</p>
  const faqPattern = /<h3[^>]*>(.*?\?)<\/h3>\s*<p[^>]*>(.*?)<\/p>/gi;
  const faqs = [];
  let match;

  while ((match = faqPattern.exec(contentHtml)) !== null) {
    const question = match[1].replace(/<[^>]*>/g, "").trim();
    const answer = match[2].replace(/<[^>]*>/g, "").trim();

    if (question.length > 10 && answer.length > 20) {
      faqs.push({
        "@type": "Question",
        name: question,
        acceptedAnswer: {
          "@type": "Answer",
          text: answer,
        },
      });
    }
  }

  if (faqs.length === 0) {
    return null;
  }

  return {
    "@type": "FAQPage",
    "@id": `${articleUrl}#faq`,
    mainEntity: faqs,
  };
}

/**
 * Merge FAQ schema into an existing article @graph array.
 * If FAQs are found, appends the FAQPage object to the graph.
 */
function mergeFaqIntoGraph(graphArray, contentHtml, articleUrl) {
  const faqSchema = extractFaqSchema(contentHtml, articleUrl);
  if (faqSchema) {
    graphArray.push(faqSchema);
  }
  return graphArray;
}

module.exports = { extractFaqSchema, mergeFaqIntoGraph };
