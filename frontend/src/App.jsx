import { useEffect, useMemo, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8001/api'

function usePlots() {
  const [plots, setPlots] = useState([])
  const [meta, setMeta] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/plots`),
      fetch(`${API_BASE}/meta`),
    ])
      .then(async ([plotsResponse, metaResponse]) => {
        if (!plotsResponse.ok) throw new Error('Failed to load plot data')
        if (!metaResponse.ok) throw new Error('Failed to load model metadata')
        const [plotsPayload, metaPayload] = await Promise.all([
          plotsResponse.json(),
          metaResponse.json(),
        ])
        setPlots(plotsPayload)
        setMeta(metaPayload)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return { plots, meta, loading, error }
}

function AppNav({ page, onNavigate, variant = 'default' }) {
  return (
    <header className={`nav-frame ${variant === 'hero' ? 'hero-nav' : ''}`}>
      <div className="brand">
        <button className="brand-button" onClick={() => onNavigate('home')}>
          <img className="brand-logo" src="/terrasset-navbar.png" alt="Terrasset" />
        </button>
      </div>
      <nav>
        {['dashboard', 'compare', 'contact'].map((item) => (
          <button key={item} className={page === item ? 'active' : ''} onClick={() => onNavigate(item)}>
            {item[0].toUpperCase() + item.slice(1)}
          </button>
        ))}
      </nav>
    </header>
  )
}

function ScoreCard({ plot, rank }) {
  return (
    <article className={`score-card ${rank === 1 ? 'best' : ''}`}>
      <span className="rank-pill">{rank} Ranked</span>
      <h3>{plot.name}</h3>
      <strong>{plot.score}/100</strong>
      <p>Environmental <b>{plot.score_breakdown.environmental_score}</b></p>
      <p>Regulatory <b>{plot.score_breakdown.regulatory_score}</b></p>
      <small>{plot.ai_summary}</small>
    </article>
  )
}

function Spectrum({ plot }) {
  if (!plot) return null
  const values = plot.mean_spectrum
  const min = Math.min(...values)
  const max = Math.max(...values)
  const points = values.map((value, index) => {
    const x = (index / (values.length - 1)) * 100
    const y = 100 - ((value - min) / (max - min || 1)) * 100
    return `${x},${y}`
  }).join(' ')
  return (
    <div className="chart-card">
      <svg viewBox="0 0 100 100" preserveAspectRatio="none">
        <polyline points={points} fill="none" stroke="#236a54" strokeWidth="1.2" />
      </svg>
    </div>
  )
}

function Home({ ranked, meta, onNavigate }) {
  const best = ranked[0]
  const updatedAt = formatUpdatedAt(meta.last_updated)
  const weights = meta.applied_weights
  return (
    <>
      <section className="home-hero">
        <video className="hero-video" autoPlay muted loop playsInline>
          <source src="" type="video/mp4" />
        </video>
        <div className="hero-overlay" />
        <div className="hero-copy">
          <h1>
            See the terrain,
            <br />
            value the asset.
          </h1>
          <p>{meta.active_use_case} screening built from hyperspectral, logistics, and regulatory signals.</p>
          <div>
            <button onClick={() => onNavigate('dashboard')}>Open dashboard</button>
            <button className="secondary" onClick={() => onNavigate('compare')}>Compare plots</button>
          </div>
        </div>
      </section>

      <section className="section-band">
        <div className="featured-investment">
          <div>
            <span>Current best candidate</span>
            <h2>{best.name}</h2>
            <p>{best.ai_summary}</p>
          </div>
          <div className="featured-metrics">
            <Metric label="Viability" value={`${best.score}/100`} />
            <Metric label="Regulatory" value={`${best.score_breakdown.regulatory_score}/100`} />
            <Metric label="Distance to sea" value={`${best.macro_infrastructure.distance_to_sea_km} km`} />
          </div>
        </div>
      </section>

      <section className="section-band">
        <SectionHeading eyebrow="Portfolio view" title="Plot ranking" />
        <div className="ranking-track">
          {ranked.map((plot, index) => <ScoreCard key={plot.name} plot={plot} rank={index + 1} />)}
        </div>
      </section>

      <section className="section-band">
        <SectionHeading eyebrow="Latest model output" title="Investment signal" />
        <div className="latest-stack">
          {ranked.slice(0, 3).map((plot, index) => (
            <LatestSignal key={plot.name} plot={plot} rank={index + 1} />
          ))}
        </div>
      </section>

      <section className="section-band">
        <SectionHeading eyebrow="What the model reads" title="Beyond visible light" />
        <div className="grid three">
          <FeatureCard title="Vegetation vigor" copy="NDVI estimates plant health and productive potential." />
          <FeatureCard title="Surface moisture" copy="NDWI helps reveal relative site moisture conditions." />
          <FeatureCard title="Spectral signature" copy="224 EnMAP bands surface patterns invisible to RGB imagery." />
        </div>
      </section>

      <section className="section-band">
        <div className="grid four stats-grid">
          <Metric label="Use case" value={meta.active_use_case} />
          <Metric label="Last updated" value={updatedAt} />
          <Metric label="Weighting" value={`${weights.environmental_weight * 100}/${weights.logistics_weight * 100}/${weights.regulatory_weight * 100}`} />
          <Metric label="Top candidate" value={best.name} />
        </div>
      </section>

      <footer className="home-footer">© 2026 Real Estate Beyond RGB</footer>
    </>
  )
}

function Dashboard({ plots }) {
  const [selectedName, setSelectedName] = useState(plots[0]?.name)
  const selected = plots.find((plot) => plot.name === selectedName) ?? plots[0]
  return (
    <>
      <Hero title="Dashboard" copy="Inspect a single plot in detail." />
      <section className="section-band selector-band">
        <PlotPicker
          eyebrow="Dashboard selection"
          title="Choose a plot to inspect"
          copy="The selected plot drives the metrics, recommendation, and spectrum below."
          value={selectedName}
          onChange={setSelectedName}
          plots={plots}
        />
      </section>
      <section className="grid three metrics">
        <Metric label="Viability score" value={`${selected.score}/100`} />
        <Metric label="Regulatory score" value={`${selected.score_breakdown.regulatory_score}/100`} />
        <Metric label="Distance to sea" value={`${selected.macro_infrastructure.distance_to_sea_km} km`} />
      </section>
      <section className="winner-card">
        <small>{selected.name} investment signal</small>
        <h2>{selected.ai_summary}</h2>
      </section>
      <section className="grid four decision-grid">
        <Metric label="NDVI" value={formatDecimal(selected.pipeline_metrics.ndvi_vegetation_vigor)} />
        <Metric label="NDWI" value={formatDecimal(selected.pipeline_metrics.ndwi_water_retention)} />
        <Metric label="Climate risk" value={selected.legal_and_risk_factors.climate_risk_flag} />
        <Metric label="Zoning" value={selected.legal_and_risk_factors.zoning_restriction} />
      </section>
      <h2>Mean spectral signature</h2>
      <Spectrum plot={selected} />
    </>
  )
}

function Compare({ plots }) {
  const [leftName, setLeftName] = useState('Veroia')
  const [rightName, setRightName] = useState('Arkadia 2')
  const left = plots.find((plot) => plot.name === leftName)
  const right = plots.find((plot) => plot.name === rightName)
  const winner = left.score >= right.score ? left : right
  return (
    <>
      <Hero title="Compare" copy="Choose two plots and compare them head to head." />
      <section className="section-band selector-band">
        <div className="grid two">
          <PlotPicker
            eyebrow="Left comparison"
            title="First plot"
            copy="The stronger baseline for the comparison."
            value={leftName}
            onChange={setLeftName}
            plots={plots}
            accent="green"
          />
          <PlotPicker
            eyebrow="Right comparison"
            title="Second plot"
            copy="Use this as the alternate investment candidate."
            value={rightName}
            onChange={setRightName}
            plots={plots}
            accent="amber"
          />
        </div>
      </section>
      <section className="versus">
        <ScoreCard plot={left} rank="A" />
        <span>VS</span>
        <ScoreCard plot={right} rank="B" />
      </section>
      <section className="winner-card">
        <small>Head-to-head prediction</small>
        <h2>{winner.name}</h2>
        <p>Recommended over the selected alternative.</p>
      </section>
      <ComparisonSection title="Score breakdown">
        <StatRow label="Overall viability" left={left.score} right={right.score} format={(v) => `${v}/100`} />
        <StatRow label="Environmental score" left={left.score_breakdown.environmental_score} right={right.score_breakdown.environmental_score} format={(v) => `${v}/100`} />
        <StatRow label="Logistics score" left={left.score_breakdown.logistics_score} right={right.score_breakdown.logistics_score} format={(v) => `${v}/100`} />
        <StatRow label="Regulatory score" left={left.score_breakdown.regulatory_score} right={right.score_breakdown.regulatory_score} format={(v) => `${v}/100`} />
      </ComparisonSection>
      <ComparisonSection title="Environmental evidence">
        <ComparisonTable
          left={left}
          right={right}
          rows={[
            ['NDVI vegetation vigor', (plot) => formatDecimal(plot.pipeline_metrics.ndvi_vegetation_vigor)],
            ['NDWI water retention', (plot) => formatDecimal(plot.pipeline_metrics.ndwi_water_retention)],
            ['Bare soil SOC index', (plot) => formatDecimal(plot.pipeline_metrics.bare_soil_soc_index)],
            ['Fused LST', (plot) => `${plot.pipeline_metrics.fused_lst_celsius.toFixed(1)} °C`],
            ['Cloud mask applied', (plot) => formatBoolean(plot.pipeline_metrics.cloud_mask_applied)],
          ]}
        />
      </ComparisonSection>
      <ComparisonSection title="Macro infrastructure">
        <ComparisonTable
          left={left}
          right={right}
          rows={[
            ['Distance to sea', (plot) => `${plot.macro_infrastructure.distance_to_sea_km} km`],
            ['Distance to high-voltage grid', (plot) => `${plot.macro_infrastructure.distance_to_high_voltage_grid_km} km`],
            ['Terrain slope', (plot) => `${plot.macro_infrastructure.terrain_slope_degrees}°`],
          ]}
        />
      </ComparisonSection>
      <ComparisonSection title="Legal and risk factors">
        <ComparisonTable
          left={left}
          right={right}
          rows={[
            ['Cadastral clearance', (plot) => plot.legal_and_risk_factors.cadastral_clearance_status],
            ['Zoning restriction', (plot) => plot.legal_and_risk_factors.zoning_restriction],
            ['Climate risk', (plot) => plot.legal_and_risk_factors.climate_risk_flag],
            ['Borehole permit difficulty', (plot) => plot.legal_and_risk_factors.borehole_permit_difficulty],
          ]}
        />
      </ComparisonSection>
      <ComparisonSection title="Location context">
        <ComparisonTable
          left={left}
          right={right}
          rows={[
            ['Latitude', (plot) => plot.coordinates.lat.toFixed(6)],
            ['Longitude', (plot) => plot.coordinates.lon.toFixed(6)],
            ['Model summary', (plot) => plot.ai_summary],
          ]}
        />
      </ComparisonSection>
    </>
  )
}

function Contact() {
  return (
    <div className="contact-page-shell">
      <Hero title="Contact" copy="Questions, feedback, or final submission details." />
      <section className="grid contact">
        <div className="panel">
          <h2>Get in touch</h2>
          <input placeholder="Your name" />
          <input placeholder="you@example.com" />
          <textarea placeholder="What's on your mind?" />
          <button>Send message</button>
        </div>
        <div className="panel">
          <h2>Future improvements</h2>
          <p>Soil quality indicators · Elevation overlays · Road access · Historical trends · Downloadable reports</p>
        </div>
      </section>
    </div>
  )
}

function Hero({ title, copy }) {
  return <section className="hero"><small>Hyperspectral investment screening</small><h1>{title}</h1><p>{copy}</p></section>
}

function Metric({ label, value }) {
  return <article className="metric"><small>{label}</small><strong>{value}</strong></article>
}

function ComparisonSection({ title, children }) {
  return (
    <section className="comparison-section">
      <h2>{title}</h2>
      {children}
    </section>
  )
}

function ComparisonTable({ left, right, rows }) {
  return (
    <div className="comparison-table">
      <div className="comparison-head">
        <span>Metric</span>
        <strong>{left.name}</strong>
        <strong>{right.name}</strong>
      </div>
      {rows.map(([label, render]) => (
        <div className="comparison-row" key={label}>
          <span>{label}</span>
          <b>{render(left)}</b>
          <b>{render(right)}</b>
        </div>
      ))}
    </div>
  )
}

function SectionHeading({ eyebrow, title }) {
  return (
    <div className="section-heading">
      <span>{eyebrow}</span>
      <h2>{title}</h2>
    </div>
  )
}

function PlotPicker({ eyebrow, title, copy, value, onChange, plots, accent = 'green' }) {
  return (
    <article className={`plot-picker ${accent === 'amber' ? 'amber' : 'green'}`}>
      <div className="plot-picker-topline" />
      <div className="plot-picker-copy">
        <span>{eyebrow}</span>
        <h2>{title}</h2>
        <p>{copy}</p>
      </div>
      <label className="plot-picker-field">
        <span>Plot</span>
        <select className="plot-select" value={value} onChange={(e) => onChange(e.target.value)}>
          {plots.map((plot) => <option key={plot.name} value={plot.name}>{plot.name}</option>)}
        </select>
      </label>
    </article>
  )
}

function FeatureCard({ title, copy }) {
  return <article className="feature-card"><h3>{title}</h3><p>{copy}</p></article>
}

function LatestSignal({ plot, rank }) {
  return (
    <article className="latest-signal">
      <span>{rank}</span>
      <strong>{plot.name}</strong>
      <i><b style={{ width: `${plot.score}%` }} /></i>
      <em>{plot.score}/100</em>
    </article>
  )
}

function StatRow({ label, left, right, format, shift = false }) {
  const leftBasis = shift ? left + 1 : left
  const rightBasis = shift ? right + 1 : right
  const total = leftBasis + rightBasis || 1
  const leftWidth = (leftBasis / total) * 100
  return (
    <article className="stat-row">
      <small>{label}</small>
      <div>
        <b>{format(left)}</b>
        <span><i style={{ width: `${leftWidth}%` }} /></span>
        <b>{format(right)}</b>
      </div>
    </article>
  )
}

function formatDecimal(value) {
  return value == null ? '—' : value.toFixed(3)
}

function formatBoolean(value) {
  return value ? 'Yes' : 'No'
}

function formatUpdatedAt(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export default function App() {
  const { plots, meta, loading, error } = usePlots()
  const [page, setPage] = useState('home')
  const ranked = useMemo(() => [...plots].sort((a, b) => b.score - a.score), [plots])
  if (loading) return <main>Loading…</main>
  if (error) return <main>{error}</main>
  return (
    <>
      {page === 'home' ? (
        <div className="home-page">
          <AppNav page={page} onNavigate={setPage} variant="hero" />
          <Home ranked={ranked} meta={meta} onNavigate={setPage} />
        </div>
      ) : (
        <main>
          <AppNav page={page} onNavigate={setPage} />
          {page === 'dashboard' && <Dashboard plots={plots} />}
          {page === 'compare' && <Compare plots={plots} />}
          {page === 'contact' && <Contact />}
        </main>
      )}
    </>
  )
}
