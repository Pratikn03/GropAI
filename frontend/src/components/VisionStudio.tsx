import React from 'react'
import { apiUpload } from '../services/api'

export default function VisionStudio(){
  const videoRef = React.useRef<HTMLVideoElement|null>(null)
  const canvasRef = React.useRef<HTMLCanvasElement|null>(null)
  const overlayRef = React.useRef<HTMLCanvasElement|null>(null)
  const [pred,setPred] = React.useState<string>('')
  const [score,setScore] = React.useState<number>(0)
  const [imgB64,setImgB64] = React.useState<string>('')

  React.useEffect(()=>{ (async ()=>{
    try{
      const stream = await navigator.mediaDevices.getUserMedia({video:true, audio:false})
      if(videoRef.current){ videoRef.current.srcObject = stream; await videoRef.current.play() }
    }catch(e){ console.error(e) }
  })() },[])

  const drawBoxes = (boxes: Array<{x1:number;y1:number;x2:number;y2:number}>)=>{
    const video = videoRef.current, overlay = overlayRef.current
    if(!video || !overlay) return
    overlay.width = video.videoWidth
    overlay.height = video.videoHeight
    const ctx = overlay.getContext('2d')!
    ctx.clearRect(0,0,overlay.width,overlay.height)
    ctx.strokeStyle = '#00FF00'
    ctx.lineWidth = 3
    boxes.forEach(box => ctx.strokeRect(box.x1, box.y1, box.x2 - box.x1, box.y2 - box.y1))
  }

  const capture = async ()=>{
    const video = videoRef.current, canvas = canvasRef.current
    if(!video || !canvas) return
    canvas.width = video.videoWidth; canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')!
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    const blob: Blob = await new Promise(r => canvas.toBlob(b => r(b!), 'image/png'))
    const form = new FormData()
    form.append('image', blob, 'frame.png')
    form.append('return_image', 'true')
    const resp = await apiUpload('/vision/infer', form)
    if(resp){
      setPred(resp.pred); setScore(resp.score)
      if(resp.image_png_b64) setImgB64('data:image/png;base64,'+resp.image_png_b64)
      if(resp.faces) drawBoxes(resp.faces)
    }
  }

  return <div>
    <h2>Vision Studio</h2>
    <div style={{position:'relative', display:'inline-block'}}>
      <video ref={videoRef} style={{maxWidth:'100%', border:'1px solid #ddd'}} muted playsInline/>
      <canvas ref={overlayRef} style={{position:'absolute', left:0, top:0}}/>
    </div>
    <div style={{marginTop:8}}>
      <button onClick={capture}>Capture & Infer</button>
      {pred && <span style={{marginLeft:12}}><b>Pred:</b> {pred} (score {score.toFixed(3)})</span>}
    </div>
    {imgB64 && <div style={{marginTop:8}}><img src={imgB64} style={{maxWidth:'100%'}}/></div>}
    <canvas ref={canvasRef} style={{display:'none'}}/>
  </div>
}
