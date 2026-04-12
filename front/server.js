const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");
const path = require("path");

const app = express();
const PORT = 3000;
const API_URL = process.env.API_URL || "http://localhost:8000";

app.use(
  "/api",
  createProxyMiddleware({
    target: API_URL,
    changeOrigin: true,
  }),
);

app.use(express.static(path.join(__dirname, "public")));

app.get("*", (_req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(PORT, () => {
  console.log(`Frontend running at http://localhost:${PORT}`);
  console.log(`Proxying /api -> ${API_URL}`);
});
