import React from 'react'
import { apiGet } from '../services/api'

export default function GovernanceScore(){
  const [score,setScore] = React.useState<number | null>(null)
  const [info,setInfo] = React.useState<any>(null)
  React.useEffect(()=>{ (async ()=>{
    const res = await apiGet('/governance/risk_score')
    setScore(res?.risk_score ?? 0)
    setInfo(res?.components)
  })() },[])
  if(score === null) return <div>Loading governance risk…</div>
  const color = score > 70 ? 'crimson' : score > 40 ? 'orange' : 'green'
  return <div style={{padding:12,border:'1px solid #ddd',borderRadius:8}}>
    <strong>Governance risk</strong><br/>
    <span style={{color}}>{score}</span>/100<br/>
    <small>
      leakage: {info?.leakage_issues ?? 0}, data: {info?.data_issues ?? 0}, images: {info?.bad_images ?? 0}
    </small>
  </div>
}
