import React from "react";
import { apiGet } from "../services/api";

export default function Health(){
  const [live,setLive]=React.useState(null);
  const [ready,setReady]=React.useState(null);
  const [ver,setVer]=React.useState(null);
  React.useEffect(()=>{
    (async()=>{
      setLive(await apiGet("/health/live"));
      setReady(await apiGet("/health/ready"));
      setVer(await apiGet("/health/version"));
    })();
  },[]);
  return (
    <div style={{display:"grid",gap:12}}>
      <div className="badge">Live: {JSON.stringify(live)}</div>
      <div className="badge">Ready: {JSON.stringify(ready)}</div>
      <div className="badge">Version: {JSON.stringify(ver)}</div>
    </div>
  );
}
