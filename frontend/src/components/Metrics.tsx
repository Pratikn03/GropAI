import React from 'react'
import { apiGet, API_BASE } from '../services/api'

export default function Metrics(){
  const [summary,setSummary] = React.useState<any>(null)
  React.useEffect(()=>{ (async ()=>{ setSummary(await apiGet('/metrics/summary')) })() },[])
  return <div>
    <h2>Metrics</h2>
    <pre>{JSON.stringify(summary, null, 2)}</pre>
    <p>CSV exports:</p>
    <ul>
      <li><a href={API_BASE + '/assets/reports/metrics/runs.csv'} target="_blank">runs.csv</a></li>
      <li><a href={API_BASE + '/assets/reports/metrics/latency_size.csv'} target="_blank">latency_size.csv</a></li>
    </ul>
    <p>Explainability gallery:</p>
    <ul>
      <li><a href={API_BASE + '/assets/reports/explain/tabular/demo/global_importance_bar.png'} target="_blank">SHAP Global Bar</a></li>
      <li><a href={API_BASE + '/assets/reports/explain/vision/'} target="_blank">Vision explain folder</a></li>
    </ul>
  </div>
}
