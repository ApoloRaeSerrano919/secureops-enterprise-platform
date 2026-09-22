import express from "express";

const app = express();
app.use(express.json({ limit: "256kb" }));
const upstream = process.env.SECUREOPS_API_URL ?? "http://api:8200";
const token = process.env.SECUREOPS_API_TOKEN ?? "analyst-token";

app.get("/health", (_req, res) => res.json({ status: "ok", service: "event-gateway" }));
app.post("/events", async (req, res) => {
  const response = await fetch(`${upstream}/events`, {
    method: "POST",
    headers: { "content-type": "application/json", authorization: `Bearer ${token}` },
    body: JSON.stringify(req.body),
  });
  const body = await response.text();
  res.status(response.status).type(response.headers.get("content-type") ?? "application/json").send(body);
});
app.listen(Number(process.env.PORT ?? 8300), "0.0.0.0", () => console.log("event-gateway listening"));
