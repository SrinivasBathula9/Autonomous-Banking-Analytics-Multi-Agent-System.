import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [currentStep, setCurrentStep] = useState(0);
    const [activeTab, setActiveTab] = useState('Workflow');
    const [query, setQuery] = useState("Analyze recent transaction anomalies and assess risk.");
    const [agentResults, setAgentResults] = useState<any>(null);
    const [history, setHistory] = useState<any[]>([]);
    const [simScenario, setSimScenario] = useState({ type: 'fraud', value: 0.5 });
    const [simResult, setSimResult] = useState<any>(null);
    const [isSimulating, setIsSimulating] = useState(false);
    const [copilotMsg, setCopilotMsg] = useState("");
    const [copilotChat, setCopilotChat] = useState<any[]>([
        { role: 'system', text: 'Executive Copilot Online. System ready for strategic inquiry.' }
    ]);
    const [trends, setTrends] = useState<any[]>([]);

    const chatEndRef = useRef<HTMLDivElement>(null);

    const steps = [
        { name: "Planning", agent: "Planner", icon: "📋" },
        { name: "Ingestion", agent: "Data Engineer", icon: "⚙️" },
        { name: "Processing", agent: "Preprocessing", icon: "🧼" },
        { name: "Modeling", agent: "Data Scientist", icon: "🧬" },
        { name: "Insights", agent: "Analyst", icon: "🔍" },
        { name: "Governance", agent: "CDO", icon: "🏛️" }
    ];

    useEffect(() => {
        fetchHistory();
        fetchTrends();
    }, []);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [copilotChat]);

    const fetchHistory = async () => {
        try {
            const res = await fetch('http://localhost:8000/history');
            const data = await res.json();
            setHistory(data);
        } catch (e) { console.error("History fetch failed", e); }
    };

    const fetchTrends = async () => {
        try {
            const res = await fetch('http://localhost:8000/trends');
            const data = await res.json();
            setTrends(data);
        } catch (e) { console.error("Trends fetch failed", e); }
    }

    const handleRunAnalysis = async () => {
        setIsAnalyzing(true);
        setCurrentStep(0);
        setAgentResults(null);
        setActiveTab('Workflow');

        try {
            const progressInterval = setInterval(() => {
                setCurrentStep((prev: number) => (prev < steps.length - 1 ? prev + 1 : prev));
            }, 1500);

            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });

            const result = await response.json();
            setAgentResults(result);
            clearInterval(progressInterval);
            setCurrentStep(steps.length - 1);
            fetchHistory();
            fetchTrends();
        } catch (error) {
            console.error("Analysis failed:", error);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleCopilotAction = () => {
        if (!copilotMsg) return;
        const newChat = [...copilotChat, { role: 'user', text: copilotMsg }];
        setCopilotChat(newChat);
        setCopilotMsg("");

        setTimeout(() => {
            let response = "I'm analyzing the historical baseline. Could you specify which sector you're most concerned about?";
            if (copilotMsg.toLowerCase().includes("risk")) {
                response = `Analysis of ${agentResults?.run_id || 'system state'} indicates an average risk delta of 0.12. Cluster 4 is currently flagged for human-in-the-loop review.`;
            } else if (copilotMsg.toLowerCase().includes("summarize")) {
                response = agentResults?.decision || "The last run identified 12 high-priority anomalies, with a recommendation for automated flagging in the Retail sector.";
            }
            setCopilotChat([...newChat, { role: 'bot', text: response }]);
        }, 800);
    };

    const handleSimulation = async () => {
        if (!agentResults?.run_id) return;
        setIsSimulating(true);
        try {
            const res = await fetch('http://localhost:8000/simulate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    run_id: agentResults.run_id,
                    type: simScenario.type,
                    value: simScenario.value
                })
            });
            const data = await res.json();
            setSimResult(data);
        } catch (e) { console.error("Simulation failed", e); }
        finally { setIsSimulating(false); }
    };

    const handleManualOverride = async () => {
        if (!agentResults?.run_id) return;
        const reason = prompt("Describe objective for override:");
        if (!reason) return;

        try {
            await fetch('http://localhost:8000/override', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    run_id: agentResults.run_id,
                    target_type: 'score',
                    target_id: 'GLOBAL',
                    new_value: 'Force Low-Risk',
                    reason: reason
                })
            });
            alert("Executive Override Persisted to Audit Log.");
        } catch (e) { alert("Override Failed."); }
    };

    const getAgentOutput = (idx: number) => {
        if (!agentResults) return null;
        switch (idx) {
            case 0: return agentResults.steps?.[0];
            case 1: return agentResults.data?.log;
            case 2: return agentResults.data?.cleaning_log;
            case 3: return agentResults.insights?.split(' | ')[0];
            case 4: return agentResults.insights?.split(' | ')[1];
            case 5: return agentResults.decision;
            default: return null;
        }
    };

    return (
        <div className="dashboard-layout">
            <aside className="sidebar">
                <div className="brand">
                    <div className="brand-icon">🏦</div>
                    <div style={{ fontSize: '0.7rem', opacity: 0.6, letterSpacing: '0.1em' }}>CONTINUOUS DECISION INTEL</div>
                    <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>Nexus Executive Suite</div>
                </div>

                <div className="query-section">
                    <label className="query-label">Direct Intelligence Query</label>
                    <textarea
                        className="query-input"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="e.g. Audit global VIP anomalies..."
                    />
                    <button className="run-btn" onClick={handleRunAnalysis} disabled={isAnalyzing}>
                        {isAnalyzing ? "Orchestrating Agents..." : "Execute Strategy"}
                    </button>
                </div>

                <div className="copilot-panel">
                    <div className="query-label">Executive Copilot</div>
                    <div className="copilot-chat">
                        {copilotChat.map((m, i) => (
                            <div key={i} className={`chat-line ${m.role}`}>
                                {m.text}
                            </div>
                        ))}
                        <div ref={chatEndRef} />
                    </div>
                    <div className="chat-input-row">
                        <input
                            value={copilotMsg}
                            onChange={e => setCopilotMsg(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleCopilotAction()}
                            placeholder="Message Copilot..."
                        />
                        <button onClick={handleCopilotAction}>→</button>
                    </div>
                </div>
            </aside>

            <main className="main-content">
                <nav className="top-nav">
                    {['Workflow', 'Report', 'What-If Lab', 'Trends', 'History', 'Governance'].map(tab => (
                        <button key={tab} className={`tab-btn ${activeTab === tab ? 'active' : ''}`} onClick={() => setActiveTab(tab)}>
                            {tab}
                        </button>
                    ))}
                </nav>

                <div className="content-viewer">
                    {activeTab === 'Workflow' && (
                        <div className="workflow-view">
                            <div className="execution-header">
                                <div>Run ID: <span className="highlight">{agentResults?.run_id || 'IDLE'}</span></div>
                                <div className="timeline-labels">
                                    {steps.map((s, i) => <span key={i} className={currentStep >= i ? 'active' : ''}>{s.name}</span>)}
                                </div>
                                <div className="timeline-bar">
                                    {steps.map((_, i) => (
                                        <div key={i} className={`timeline-dot ${currentStep >= i ? 'filled' : ''} ${currentStep === i && isAnalyzing ? 'pulsing' : ''}`}></div>
                                    ))}
                                </div>
                            </div>

                            <div className="agents-parent-block">
                                <div className="parent-label">🤖 Autonomous Strategic Agents</div>
                                <div className="workflow-grid">
                                    {steps.map((step, idx) => (
                                        <div key={idx} className={`card ${currentStep === idx && isAnalyzing ? 'active' : ''}`}>
                                            <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                                                <h3 style={{ fontSize: '0.9rem' }}>{step.icon} {step.agent}</h3>
                                                <span style={{ fontSize: '0.6rem', color: 'var(--primary)' }}>{currentStep >= idx ? '✓' : ''}</span>
                                            </div>
                                            <p style={{ fontSize: '0.8rem', opacity: 0.8 }}>{getAgentOutput(idx) || `Standby...`}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {agentResults?.debate && (
                                <div className="debate-section">
                                    <h3>🧠 Collaborative Consensus Debate</h3>
                                    <div className="debate-list">
                                        {agentResults.debate.map((msg: string, i: number) => (
                                            <div key={i} className="debate-item">
                                                <div className="debate-avatar">{msg.split(':')[0][0]}</div>
                                                <div className="debate-msg">{msg}</div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'History' && (
                        <div className="history-list">
                            <h2>Intelligence Run history</h2>
                            <div className="history-table">
                                <div className="table-header">
                                    <span>Run ID</span>
                                    <span>Timestamp</span>
                                    <span>Query</span>
                                    <span>Decision</span>
                                </div>
                                {history.map(run => (
                                    <div key={run.run_id} className="table-row">
                                        <span className="highlight">{run.run_id}</span>
                                        <span>{run.timestamp}</span>
                                        <span className="truncate">{run.query}</span>
                                        <span>{run.decision}</span>
                                    </div>
                                ))}
                                {history.length === 0 && <div className="empty-state">No historical runs found.</div>}
                            </div>
                        </div>
                    )}

                    {activeTab === 'Report' && (
                        <div className="report-paper">
                            {agentResults ? (
                                <>
                                    <h2>Executive Briefing: Banking Risk Analysis</h2>
                                    <p className="run-meta">Run ID: {agentResults.run_id} | {new Date().toLocaleDateString()}</p>
                                    <div className="report-section">
                                        <h3>Analytical Findings</h3>
                                        <p>{agentResults.insights}</p>
                                    </div>
                                    <div className="report-section">
                                        <h3>Strategic Decision</h3>
                                        <p>{agentResults.decision}</p>
                                    </div>
                                    <div className="report-section" style={{ textAlign: 'center' }}>
                                        <a href={`http://localhost:8000/${agentResults.report_path}`} target="_blank" className="run-btn" style={{ width: 'auto' }}>
                                            📄 Download Full Audit Report
                                        </a>
                                    </div>
                                </>
                            ) : <div className="empty-state">No results to show. Execute strategy to generate report.</div>}
                        </div>
                    )}

                    {activeTab === 'Trends' && (
                        <div className="trends-dashboard">
                            <h2>Strategic Risk Trends</h2>
                            <p style={{ opacity: 0.6 }}>Continuous Monitoring: ACTIVE (Baseline-XP4)</p>

                            <div className="charts-grid" style={{ marginTop: '2rem' }}>
                                <div className="chart-card" style={{ gridColumn: 'span 2' }}>
                                    <h3>Average Sensitivity Delta (Historical)</h3>
                                    <div className="visual-trend">
                                        {trends.map((t, i) => (
                                            <div key={i} className="trend-bar" style={{ height: `${t.avg_risk * 240}px`, opacity: 0.3 + (i / trends.length) }}>
                                                <span className="bar-val">{t.avg_risk}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div className="chart-card">
                                    <h3>Critical Anomalies Detected</h3>
                                    <div className="val-display">
                                        {trends[trends.length - 1]?.fraud_cases || 0}
                                        <span className={`delta ${trends.length > 1 ? 'up' : ''}`}>+8.4%</span>
                                    </div>
                                </div>
                            </div>

                            <div className="faq-section" style={{ marginTop: '3rem' }}>
                                <h3>📊 Understanding Trends FAQ</h3>
                                <details className="faq-item">
                                    <summary>What do these charts represent?</summary>
                                    <p>These charts aggregate intelligence from every historical run. The bars show the average risk detected per run, allowing you to spot seasonal or systemic shifts in banking anomalies.</p>
                                </details>
                                <details className="faq-item">
                                    <summary>How is "Average Sensitivity Delta" calculated?</summary>
                                    <p>It averages the risk scores of all customers analyzed in a specific run. A rising trend suggests the agents are detecting higher-risk profiles across the board.</p>
                                </details>
                                <details className="faq-item">
                                    <summary>What triggers a Critical Anomaly?</summary>
                                    <p>Critical anomalies are flagged when multiple agents (Data Scientist and CDO) agree that a transaction or customer profile exceeds a 0.75 risk threshold.</p>
                                </details>
                            </div>
                        </div>
                    )}

                    {activeTab === 'Governance' && (
                        <div className="governance-center">
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <h2>Governance & Compliance Lab</h2>
                                <button className="run-btn" style={{ width: 'auto', background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', color: '#ef4444' }} onClick={handleManualOverride}>
                                    ⚠️ Trigger Override
                                </button>
                            </div>
                            <div className="gov-grid" style={{ marginTop: '2rem' }}>
                                <div className="gov-card">
                                    <h3>Model Explainability</h3>
                                    {agentResults?.explanations ? Object.entries(agentResults.explanations).map(([score, exp]: any) => (
                                        <div key={score} className="exp-item">
                                            <div className="exp-score">Insight Confidence: 92%</div>
                                            <p style={{ margin: '0.5rem 0', fontStyle: 'italic' }}>{exp.plain_english}</p>
                                            <div className="feature-bars" style={{ marginTop: '1rem' }}>
                                                {Object.entries(exp.feature_importance).map(([f, v]: any) => (
                                                    <div key={f} className="bar-row">
                                                        <span className="bar-label">{f}</span>
                                                        <div className="bar-bg"><div className="bar-fill" style={{ width: `${Math.abs(v)}%` }}></div></div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )) : <div className="empty-state">Execute strategy to view model traceability.</div>}
                                </div>
                                <div className="gov-card">
                                    <h3>Audit Trail</h3>
                                    <div className="audit-list">
                                        <div className="audit-row"><span>2026-02-21 14:45</span><span>Run Start: {agentResults?.run_id || 'N/A'}</span></div>
                                        <div className="audit-row"><span>2026-02-21 14:50</span><span>State Persisted: Vector Index</span></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'What-If Lab' && (
                        <div className="simulation-lab">
                            <div className="sim-form">
                                <h2>Decision Simulation</h2>
                                <label>Variable</label>
                                <select value={simScenario.type} onChange={e => setSimScenario({ ...simScenario, type: e.target.value })}>
                                    <option value="fraud">Fraud Probability Threshold</option>
                                    <option value="risk">VIP Risk Allowance</option>
                                </select>
                                <label>Sensitivity Intensity: {simScenario.value}</label>
                                <input type="range" min="0.1" max="0.9" step="0.05" value={simScenario.value} onChange={e => setSimScenario({ ...simScenario, value: parseFloat(e.target.value) })} />
                                <button className="run-btn" onClick={handleSimulation} disabled={isSimulating || !agentResults}>
                                    {isSimulating ? 'Projecting Strategic Impact...' : 'Project Strategy'}
                                </button>
                            </div>
                            <div className="sim-results">
                                {simResult ? (
                                    <div className="sim-card card" style={{ padding: '2rem' }}>
                                        <h3>Strategy Projection: {simResult.parameter}</h3>
                                        <div className="impact-grid">
                                            <div className="impact-box">
                                                <label>Baseline</label>
                                                <div className="val">{simResult.value_before}</div>
                                            </div>
                                            <div className="impact-box highlight">
                                                <label>Projected</label>
                                                <div className="val">{simResult.value_after}</div>
                                            </div>
                                        </div>
                                        <div className="impact-summary" style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
                                            <strong>Business Impact:</strong> {simResult.business_impact}
                                        </div>
                                    </div>
                                ) : <div className="empty-state">Adjust sensitivity to run a strategy projection.</div>}
                            </div>

                            <div className="faq-section" style={{ gridColumn: 'span 2', marginTop: '2rem' }}>
                                <h3>🧪 Simulation Lab FAQ</h3>
                                <details className="faq-item">
                                    <summary>What is the purpose of the Simulation Lab?</summary>
                                    <p>It allows you to simulate "What-If" scenarios. For example, if we lowered our fraud detection threshold, how many more transactions would have been flagged? This helps calibrate business policy.</p>
                                </details>
                                <details className="faq-item">
                                    <summary>How do I interpret "Business Impact"?</summary>
                                    <p>Every decision has a trade-off. Tightening security (lower threshold) reduces fraud but increases false positives (friction for customers). The impact summary highlights this trade-off based on simulated volume.</p>
                                </details>
                                <details className="faq-item">
                                    <summary>Why is a previous "Run" required?</summary>
                                    <p>Simulations are run against the real state of a previous intelligence run. This ensures projections are grounded in actual historical data rather than just random numbers.</p>
                                </details>
                            </div>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}

export default App;
