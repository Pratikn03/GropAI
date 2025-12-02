import React from "react";
import { apiPost } from "../services/api";

export default function Chat(){
  const [q,setQ] = React.useState("how do we deploy");
  const [ans,setAns] = React.useState<any>(null);
  const [busy,setBusy] = React.useState(false);

  const ask = async()=>{
    setBusy(true);
    try { setAns(await apiPost("/chat/ask",{query:q, top_k:5})); }
    finally { setBusy(false); }
  };

  return (
    <div style={{display:"grid",gap:12}}>
      <div className="input-row">
        <input className="input" value={q} onChange={e=>setQ(e.target.value)} placeholder="Ask the system (RAG)…"/>
        <button className="btn" onClick={ask} disabled={busy}>{busy ? "Thinking…" : "Ask"}</button>
        <button className="btn ghost" onClick={()=>setAns(null)}>Clear</button>
      </div>
      {ans && (
        <div className="card" style={{background:"var(--panel-2)"}}>
          <div className="card-body">
            <div style={{fontWeight:700,marginBottom:8}}>Answer</div>
            <pre style={{background:"transparent",whiteSpace:"pre-wrap",margin:0,fontFamily:"ui-monospace,Menlo,Consolas"}}>
{JSON.stringify(ans.answer ?? ans, null, 2)}
            </pre>
            {!!ans.citations?.length && (
              <div style={{marginTop:12}}>
                <div style={{color:"var(--muted)",fontSize:13}}>Sources</div>
                <ul style={{margin:0,paddingLeft:16}}>
                  {ans.citations.map((source:any)=><li key={source.rank}><strong>{source.title}</strong> — score {source.score.toFixed(3)}</li>)}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
