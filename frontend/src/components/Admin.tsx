import React from "react";
import { apiGet } from "../services/api";

export default function Admin(){
  const [info,setInfo]=React.useState(null);
  React.useEffect(()=>{ (async()=>setInfo(await apiGet("/models/info")))() },[]);
  return (
    <div className="card" style={{background:"var(--panel-2)"}}>
      <div className="card-body">
        <div style={{fontWeight:700,marginBottom:8}}>Models</div>
        <pre style={{background:"transparent",whiteSpace:"pre-wrap",margin:0,fontFamily:"ui-monospace,Menlo,Consolas"}}>
          {JSON.stringify(info,null,2)}
        </pre>
      </div>
    </div>
  );
}
