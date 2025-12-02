import React from 'react'
import { apiGet } from '../services/api'

type DatasetSummary = {
  name: string
  type?: string
  task?: string
  path_hint?: string
  config_file?: string
  error?: string
}

type ApiResponse = {
  datasets?: DatasetSummary[]
}

const tableStyle: React.CSSProperties = {
  width: '100%',
  borderCollapse: 'collapse',
  background: '#fff',
  borderRadius: 8,
  boxShadow: '0 2px 8px rgba(15,23,42,0.08)'
}

const headerCell: React.CSSProperties = {
  textAlign: 'left',
  padding: '12px 16px',
  borderBottom: '1px solid #e2e8f0',
  fontSize: 14,
  fontWeight: 600,
  color: '#475569'
}

const bodyCell: React.CSSProperties = {
  padding: '12px 16px',
  borderBottom: '1px solid #f1f5f9',
  fontSize: 14,
  color: '#0f172a'
}

export default function Datasets(){
  const [items, setItems] = React.useState<DatasetSummary[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        const response: ApiResponse | null = await apiGet('/features/datasets')
        if (mounted) {
          setItems(response?.datasets ?? [])
        }
      } catch (err) {
        console.error('Failed to load datasets', err)
        if (mounted) {
          setError('Unable to fetch dataset registry. Please retry.')
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    })()
    return () => {
      mounted = false
    }
  }, [])

  if (loading) {
    return <p>Loading dataset registry…</p>
  }

  if (error) {
    return <p style={{color: '#b91c1c'}}>{error}</p>
  }

  if (items.length === 0) {
    return <p>No datasets registered yet. Add YAML configs under <code>configs/datasets</code>.</p>
  }

  return (
    <div>
      <h2 style={{marginBottom: 16}}>Dataset Registry</h2>
      <div style={{overflowX: 'auto'}}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={headerCell}>Name</th>
              <th style={headerCell}>Type</th>
              <th style={headerCell}>Task</th>
              <th style={headerCell}>Path hint</th>
              <th style={headerCell}>Config</th>
              <th style={headerCell}>Status</th>
            </tr>
          </thead>
          <tbody>
            {items.map((dataset) => (
              <tr key={dataset.name}>
                <td style={bodyCell}>{dataset.name}</td>
                <td style={bodyCell}>{dataset.type ?? '—'}</td>
                <td style={bodyCell}>{dataset.task ?? '—'}</td>
                <td style={bodyCell}>{dataset.path_hint ?? '—'}</td>
                <td style={bodyCell}>
                  {dataset.config_file ? (
                    <code>{dataset.config_file}</code>
                  ) : (
                    '—'
                  )}
                </td>
                <td style={{...bodyCell, color: dataset.error ? '#b91c1c' : '#10b981'}}>
                  {dataset.error ?? 'ok'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
