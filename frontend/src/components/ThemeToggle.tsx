import React from "react";

export default function ThemeToggle(){
  const [theme,setTheme]=React.useState(
    document.documentElement.getAttribute("data-theme") || "dark"
  );
  const toggle=()=>{
    const next=theme==="dark"?"light":"dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("socialsense-theme", next);
    setTheme(next);
  };
  return (
    <button className="btn ghost" onClick={toggle} aria-label="Toggle theme">
      {theme==="dark"?"🌙 Dark":"☀️ Light"}
    </button>
  );
}
