import React from 'react'
import { apiPost } from '../services/api'

type Citation = { title: string; url: string; score: number }

export default function Chat(){
  const [query,setQuery] = React.useState('')
  const [answer,setAnswer] = React.useState('')
  const [cits,setCits] = React.useState<Citation[]>([])

  const ask = async ()=>{
    const res = await apiPost('/chat/ask', {query, top_k: 5})
    setAnswer(res?.answer ?? '')
    setCits(res?.citations ?? [])
    setQuery('')
  }

  return <div>
    <h2>Chat</h2>
    <div style={{display:'flex', gap:8}}>
      <input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Ask..." style={{flex:1}} />
      <button onClick={ask}>Send</button>
    </div>
    {answer && <div style={{marginTop:8}}><b>Answer:</b><div style={{whiteSpace:'pre-wrap'}}>{answer}</div></div>}
    {cits.length>0 && <div style={{marginTop:8}}>
      <b>Citations:</b>
      <ul>
        {cits.map((cit,i)=><li key={i}>{cit.url ? <a href={cit.url} target="_blank">{cit.title}</a> : cit.title} (score {cit.score.toFixed(3)})</li>)}
      </ul>
    </div>}
  </div>
}
