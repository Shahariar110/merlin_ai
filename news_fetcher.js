const express = require("express");
const axios = require("axios");
const { JSDOM } = require("jsdom");
const { Readability } = require("@mozilla/readability");

const app = express();
const PORT = 3000; // Choose a port for the API server

app.get("/fetch-article", async (req, res) => {
  const { keyword } = req.query;

  if (!keyword) {
    return res.status(400).json({ error: "Keyword is required." });
  }

  const apiKey = "6e96720762f847438e881106435d6aca"; 
  const apiUrl = `https://newsapi.org/v2/everything?q=${keyword}&sortBy=publishedAt&language=en&apiKey=${apiKey}`;

  try {
    // Fetch articles from NewsAPI
    const response = await axios.get(apiUrl);
    const articles = response.data.articles;

    if (articles.length === 0) {
      return res.status(404).json({ error: "No articles found for the given keyword." });
    }

    // Extract details of the first article
    const firstArticle = articles[0];
    const articleResponse = await axios.get(firstArticle.url);
    const dom = new JSDOM(articleResponse.data, { url: firstArticle.url });
    const reader = new Readability(dom.window.document);
    const article = reader.parse();

    if (article) {
      res.json({
        title: firstArticle.title,
        description: firstArticle.description,
        url: firstArticle.url,
        content: article.textContent,
      });
    } else {
      res.status(500).json({ error: "Unable to extract article content." });
    }
  } catch (error) {
    console.error("Error fetching or parsing the article:", error.message);
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running at http://localhost:${PORT}`);
});
