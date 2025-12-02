import React from "react";
import ThemeToggle from "./ThemeToggle";

type Props = { children: React.ReactNode; route: string };

export default function Layout({ children, route }: Props){
  return (
    <>
      <header className="nav">
        <div className="container nav-inner">
          <div className="brand">
            <span className="logo" aria-hidden />
            <span>SocialSense SLM</span>
            <span className="badge">v2.6</span>
          </div>
          <nav className="nav-links">
            <a href="#/" className={route==="#/"?"active":""}>Chat</a>
            <a href="#/datasets" className={route==="#/datasets"?"active":""}>Datasets</a>
            <a href="#/admin" className={route==="#/admin"?"active":""}>Admin</a>
            <a href="#/health" className={route==="#/health"?"active":""}>Health</a>
          </nav>
          <div className="nav-spacer"/>
          <ThemeToggle />
        </div>
      </header>
      <main className="container wrap">
        {children}
      </main>
      <footer className="footer container">
        © {new Date().getFullYear()} SocialSense — Leakage-audited, privacy-tunable ML.
      </footer>
    </>
  );
}
