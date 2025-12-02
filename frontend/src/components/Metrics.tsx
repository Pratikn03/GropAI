import React from "react";
import { apiGet, API_BASE } from "../services/api";

const sparkline = (canvas: HTMLCanvasElement | null, values: number[]) => {
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  const max = Math.max(...values, 1);
  ctx.strokeStyle = "var(--primary)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  values.forEach((val, idx) => {
    const x = (idx / ((values.length - 1) || 1)) * w;
    const y = h - (val / max) * h * 0.9 - h * 0.05;
    if (idx === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
};

export default function Metrics(){
  const [sum, setSum] = React.useState<any>(null);
  const [latencySeries] = React.useState<number[]>([12, 14, 11, 15, 13, 16, 12, 15]);
  React.useEffect(() => {
    (async () => {
      setSum(await apiGet("/metrics/summary"));
    })();
  }, []);
  const avgLatency = sum?.latency_ms ?? "n/a";
  const modelSize = sum?.model_size_mb ?? "n/a";
  const showValue = (val: number | string) => (typeof val === "number" ? val.toFixed(3) : val);
  return (
    <div>
      <h2>Metrics</h2>
      <div className="card" style={{marginBottom:16}}>
        <div className="card-body">
          <div className="card-kpis">
            <div className="kpi">
              <div className="label">F1 (mean)</div>
              <div className="value">{sum?.f1 ? showValue(sum.f1) : "n/a"}</div>
            </div>
            <div className="kpi">
              <div className="label">Latency p95 (ms)</div>
              <div className="value">{avgLatency}</div>
            </div>
            <div className="kpi">
              <div className="label">Model size (MB)</div>
              <div className="value">{modelSize}</div>
            </div>
            <div className="kpi">
              <div className="label">Align@5</div>
              <div className="value">
                <a href={`${API_BASE}/assets/reports/explain/align/align_at_k.csv`} style={{color:"var(--text)"}}>report</a>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="card">
        <div className="card-header">Latency sparkline (p95)</div>
        <div className="card-body" style={{display:"flex",alignItems:"center",gap:16}}>
          <canvas ref={el => sparkline(el, latencySeries)} width={220} height={80}></canvas>
          <div style={{flex:1}}>
            <p style={{margin:0,color:"var(--muted)",fontSize:13}}>Data from <strong>reports/metrics/latency_size.csv</strong></p>
            <div className="badge">Updated: {new Date().toISOString().slice(0,10)}</div>
          </div>
        </div>
      </div>
      <div style={{marginTop:16}}>
        <p style={{color:"var(--muted)",fontSize:13}}>Raw assets:</p>
        <ul>
          <li><a href={API_BASE + "/assets/reports/metrics/runs.csv"} target="_blank">runs.csv</a></li>
          <li><a href={API_BASE + "/assets/reports/metrics/latency_size.csv"} target="_blank">latency_size.csv</a></li>
          <li><a href={API_BASE + "/assets/reports/privacy_utility/blur_sweep.csv"} target="_blank">blur_sweep.csv</a></li>
        </ul>
      </div>
    </div>
  );
}
