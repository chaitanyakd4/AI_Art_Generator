import React from "react";
import "./globals.css"; // ✅ Correct path for Next.js App Router

const Layout = ({ children }: { children: React.ReactNode }) => {
  return <div className="min-h-screen">{children}</div>;
};

export default Layout;
