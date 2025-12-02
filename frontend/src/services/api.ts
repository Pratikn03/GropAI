export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function apiPost(path: string, body: any){
  const res = await fetch(API_BASE + path, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(body)
  })
  try{ return await res.json() }catch{ return null }
}

export async function apiUpload(path: string, formData: FormData){
  const res = await fetch(API_BASE + path, { method:'POST', body: formData })
  try{ return await res.json() }catch{ return null }
}

export async function apiGet(path: string){
  const res = await fetch(API_BASE + path)
  try{ return await res.json() }catch{ return null }
}
