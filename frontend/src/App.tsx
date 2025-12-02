import React from "react";
import "./styles/app.css";
import "./styles/modern.css";
import Chat from "./components/Chat";
import Datasets from "./components/Datasets";
import FeaturesInfo from "./components/FeaturesInfo";
import GovernanceScore from "./components/GovernanceScore";
import Layout from "./components/Layout";
import Health from "./components/Health";
import Admin from "./components/Admin";

const workspaceSections = {
  "#/": <Chat />,
  "#/datasets": <Datasets />,
  "#/health": <Health />,
  "#/admin": <Admin />,
};

export default function App(){
  const [hash,setHash]=React.useState(window.location.hash || "#/");
  React.useEffect(()=>{
    const listener=() => setHash(window.location.hash || "#/");
    window.addEventListener("hashchange", listener);
    return () => window.removeEventListener("hashchange", listener);
  },[]);

  const mainContent = workspaceSections[hash] ?? <Chat />;

  return (
    <Layout route={hash}>
      <div className="grid">
        <section className="card">
          <div className="card-header">
            <svg className="icon" viewBox="0 0 24 24" fill="currentColor"><path d="M5 12l5 5L20 7"/></svg>
            System Status
          </div>
          <div className="card-body">
            <div className="card-kpis" style={{marginBottom:12}}>
              <div className="kpi">
                <div className="label">Governance Risk</div>
                <div className="value"><GovernanceScore/></div>
              </div>
              <div className="kpi">
                <div className="label">Feature Store</div>
                <div className="value"><FeaturesInfo/></div>
              </div>
            </div>
            <div style={{fontSize:13,color:"var(--muted)"}}>
              SBERT RAG, LightGBM HPO, SHAP batch, ONNX CV path.
            </div>
          </div>
        </section>

        <section className="card">
          <div className="card-header">
            <svg className="icon" viewBox="0 0 24 24" fill="currentColor"><path d="M3 5h18v2H3zm0 6h18v2H3zm0 6h18v2H3z"/></svg>
            Workspace
          </div>
          <div className="card-body">
            {mainContent}
          </div>
        </section>
      </div>
    </Layout>
  );
}
