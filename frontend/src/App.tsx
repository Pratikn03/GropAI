import React from 'react'
import Chat from './components/Chat'
import VisionStudio from './components/VisionStudio'
import AudioStudio from './components/AudioStudio'
import Metrics from './components/Metrics'
import PrivacyConsent from './components/PrivacyConsent'
import Datasets from './components/Datasets'
import FeaturesInfo from './components/FeaturesInfo'
import GovernanceScore from './components/GovernanceScore'

const columnStyle: React.CSSProperties = {display:'flex', gap:16, flexWrap:'wrap'}
const card: React.CSSProperties = {flex:'1 1 320px', padding:16, border:'1px solid #ddd', borderRadius:8, background:'#fff'}

function ControlRoom(){
  return (
    <>
      <div style={columnStyle}>
        <section style={card}><VisionStudio/></section>
        <section style={card}><AudioStudio/></section>
        <section style={card}><Chat/></section>
      </div>
      <div style={{...columnStyle, marginTop:24}}>
        <section style={card}><Metrics/></section>
        <section style={card}><PrivacyConsent/></section>
        <section style={card}><FeaturesInfo/></section>
        <section style={card}><GovernanceScore/></section>
      </div>
    </>
  )
}

export default function App(){
  const [route, setRoute] = React.useState<string>(() => window.location.hash || '#/')

  React.useEffect(() => {
    const handleHash = () => setRoute(window.location.hash || '#/')
    window.addEventListener('hashchange', handleHash)
    return () => window.removeEventListener('hashchange', handleHash)
  }, [])

  const active = route === '#/datasets' ? 'datasets' : 'dashboard'
  const navLink = (href: string, label: string) => (
    <a
      key={href}
      href={href}
      style={{
        textDecoration: 'none',
        fontWeight: active === label.toLowerCase() ? 600 : 500,
        color: active === label.toLowerCase() ? '#0f172a' : '#475569'
      }}
    >
      {label}
    </a>
  )

  let content: React.ReactNode = <ControlRoom/>
  if (active === 'datasets') {
    content = <Datasets/>
  }

  return (
    <div style={{padding:24, fontFamily:'system-ui', background:'#f5f5f5', minHeight:'100vh'}}>
      <header style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:24}}>
        <h1 style={{margin:0}}>SocialSense Control Room</h1>
        <nav style={{display:'flex', gap:16}}>
          {navLink('#/', 'Dashboard')}
          <span style={{color:'#cbd5f5'}}>|</span>
          {navLink('#/datasets', 'Datasets')}
        </nav>
      </header>
      {content}
    </div>
  )
}
