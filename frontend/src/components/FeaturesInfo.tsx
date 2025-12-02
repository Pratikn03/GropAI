import React from 'react'
import { apiGet } from '../services/api'

export default function FeaturesInfo(){
  const [info,setInfo] = React.useState<any>(null)
  React.useEffect(()=>{ (async ()=> setInfo(await apiGet('/features/info')))() },[])
  if(!info) return <div>Loading feature store info…</div>
  const latest = info.latest || {}
  return <div style={{padding:12,border:'1px solid #ddd',borderRadius:8,marginBottom:8}}>
    <strong>Feature Store</strong><br/>
    Active version: {info.active_version || 'n/a'}<br/>
    Latest snapshot: {latest.date || 'n/a'} | {latest.size_mb ?? '-'} MB | {latest.rows ?? '-'} rows
  </div>
}
