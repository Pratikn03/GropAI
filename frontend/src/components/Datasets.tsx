import React from "react";
import { apiGet } from "../services/api";

export default function Datasets(){
  const [items,setItems]=React.useState<any[]>([]);
  React.useEffect(()=>{
    (async()=>{
      const res = await apiGet("/features/datasets");
      setItems(res?.datasets || []);
    })();
  },[]);
  return (
    <div style={{display:"grid",gap:12}}>
      <table className="table">
        <thead>
          <tr><th>Name</th><th>Config</th><th>Type</th><th>Task</th></tr>
        </thead>
        <tbody>
          {items.map((d,i)=>(
            <tr key={i}>
              <td><strong>{d.name}</strong></td>
              <td style={{color:"var(--muted)"}}>{d.config_file}</td>
              <td>{d.type ?? "-"}</td>
              <td>{d.task ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {!items.length && <div className="badge">No datasets registered yet.</div>}
    </div>
  );
}
