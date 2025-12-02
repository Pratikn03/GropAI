import React from "react";
import { apiGet } from "../services/api";

export default function FeaturesInfo(){
  const [info,setInfo] = React.useState<any>(null);
  React.useEffect(()=>{ (async()=>setInfo(await apiGet("/features/info")))() },[]);
  const latest = info?.latest || {};
  if(!info) return <div>Loading feature store info…</div>;
  return (
    <div style={{display:"grid",gap:8}}>
      <div className="badge">Active: {info.active_version ?? "-"}</div>
      <div style={{fontSize:13,color:"var(--muted)"}}>
        Latest snapshot: <span style={{fontWeight:600}}>{latest.date ?? "-"}</span> · {latest.size_mb ?? "-"} MB · rows {latest.rows ?? "-"}
      </div>
    </div>
  );
}
