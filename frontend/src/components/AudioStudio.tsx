import React from 'react'
import { apiUpload } from '../services/api'

export default function AudioStudio(){
  const [recorder,setRecorder] = React.useState<MediaRecorder|null>(null)
  const chunks = React.useRef<Blob[]>([])
  const [transcript,setTranscript] = React.useState('')

  const start = async ()=>{
    const stream = await navigator.mediaDevices.getUserMedia({audio:true, video:false})
    const mr = new MediaRecorder(stream, {mimeType:'audio/webm'})
    mr.ondataavailable = e=>{ if(e.data.size>0) chunks.current.push(e.data) }
    mr.onstop = async ()=>{
      const blob = new Blob(chunks.current,{type:'audio/webm'})
      chunks.current = []
      const fd = new FormData()
      fd.append('audio', blob, 'clip.webm')
      fd.append('sample_rate', '16000')
      const res = await apiUpload('/audio/asr', fd)
      if(res?.text) setTranscript(res.text)
    }
    setRecorder(mr)
    mr.start()
  }

  const stop = ()=>{ recorder?.stop(); setRecorder(null) }

  return <div>
    <h2>Audio Studio</h2>
    {!recorder && <button onClick={start}>Start Recording</button>}
    {recorder && <button onClick={stop}>Stop & Transcribe</button>}
    {transcript && <p><b>ASR:</b> {transcript}</p>}
  </div>
}
