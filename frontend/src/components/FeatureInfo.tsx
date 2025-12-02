import React from 'react'
import { apiGet } from '../services/api'

type Snapshot = {
  date?: string
  path?: string
  size_mb?: number | null
  rows?: number | null
}

type FeatureInfoResponse = {
  active_version?: string | null
  latest?: Snapshot | null
}

export default function FeatureInfo(){
  const [data, setData] = React.useState<FeatureInfoResponse | null>(null)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        const resp = await apiGet('/features/info')
        if (mounted) {
          setData(resp)
        }
      } catch (err) {
        console.warn('Failed to load feature info', err)
        if (mounted) {
          setError('Unable to reach feature API')
        }
      }
    })()
    return () => {
      mounted = false
    }
  }, [])

  const latest = data?.latest
  return (
    <div>
      <h3 style={{marginTop: 0}}>Feature Store</h3>
      <p style={{margin: '8px 0', color: '#475569'}}>
        Active version: <strong>{data?.active_version ?? 'unknown'}</strong>
      </p>
      {error && <p style={{color: '#b91c1c'}}>{error}</p>}
      {!error && !latest && <p style={{color: '#94a3b8'}}>No snapshots published yet.</p>}
      {latest && (
        <dl style={{display: 'grid', gridTemplateColumns: '120px 1fr', rowGap: 8, columnGap: 12, margin: 0, fontSize: 14}}>
          <dt style={{color: '#94a3b8'}}>Date</dt>
          <dd style={{margin: 0}}>{latest.date ?? '—'}</dd>
          <dt style={{color: '#94a3b8'}}>Size</dt>
          <dd style={{margin: 0}}>{latest.size_mb ? `${latest.size_mb} MB` : '—'}</dd>
          <dt style={{color: '#94a3b8'}}>Rows</dt>
          <dd style={{margin: 0}}>{latest.rows ?? '—'}</dd>
          <dt style={{color: '#94a3b8'}}>Path</dt>
          <dd style={{margin: 0, fontFamily: 'monospace', fontSize: 12}}>{latest.path ?? '—'}</dd>
        </dl>
      )}
    </div>
  )
}
