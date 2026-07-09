import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/layout/AppShell";
import { AuthProvider } from "@/lib/auth-context";

export const metadata: Metadata = {
  title: "AI Quant Research Hub | AI量化研究平台",
  description: "AI驱动的股票量化分析、策略评分、回测分析及可视化报告平台",
  keywords: ["量化投资", "股票分析", "AI投资", "量化研究", "回测系统"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" className="dark">
      <body className="min-h-screen">
        <AuthProvider>
          <AppShell>{children}</AppShell>
        </AuthProvider>
      </body>
    </html>
  );
}
