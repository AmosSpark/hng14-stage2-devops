const express = require("express");
const axios = require("axios");
const path = require("path");
const app = express();

const API_URL = process.env.API_URL;

if (!API_URL) {
  console.error("API_URL is required");
  process.exit(1);
}

app.use(express.json());
app.use(express.static(path.join(__dirname, "views")));

app.post("/submit", async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`);
    res.json(response.data);
  } catch (err) {
    const status = err.response?.status || 500;
    res.status(status).json({ error: "something went wrong" });
  }
});

app.get("/status/:id", async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`);
    res.json(response.data);
  } catch (err) {
    const status = err.response?.status || 500;
    const message = status === 404 ? "job not found" : "something went wrong";
    res.status(status).json({ error: message });
  }
});

app.listen(3000, () => {
  console.log("Frontend running on port 3000");
});
