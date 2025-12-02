import React from 'react'
import { apiPost, apiGet } from '../services/api'

export default function PrivacyConsent(){
  const [consent,setConsent] = React.useState(false)
  React.useEffect(()=>{ (async ()=>{ const res = await apiGet('/privacy/consent'); setConsent(!!res?.enabled) })() },[])
  const toggle = async ()=>{
    const res = await apiPost('/privacy/consent', {enabled: !consent})
    if(res?.status === 'ok') setConsent(!consent)
  }
  return <div>
    <h2>Privacy & Consent</h2>
    <p>Consent is <b>{consent ? 'ON' : 'OFF'}</b></p>
    <button onClick={toggle}>{consent ? 'Disable' : 'Enable'} consent</button>
  </div>
}
