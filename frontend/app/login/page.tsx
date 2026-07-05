"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth, ApiError } from "@/lib/auth-context";
import { Lock, User, Mail, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login, register } = useAuth();

  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      if (mode === "login") {
        await login(username, password);
      } else {
        await register(username, password, email || undefined);
      }
      router.push("/");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError(mode === "login" ? "登录失败，请检查用户名和密码" : "注册失败");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center gap-2">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-purple-500">
            <span className="text-lg font-bold text-white">AI</span>
          </div>
          <h1 className="font-display text-xl font-semibold">AIQRH</h1>
          <p className="text-sm text-muted-foreground">AI 量化研究平台</p>
        </div>

        <Card>
          <CardContent className="p-6">
            <div className="mb-6 flex rounded-xl border border-white/10 p-1">
              <button
                type="button"
                className={`flex-1 rounded-lg py-2 text-sm font-medium transition-colors ${
                  mode === "login" ? "bg-primary/10 text-primary" : "text-muted-foreground"
                }`}
                onClick={() => {
                  setMode("login");
                  setError(null);
                }}
              >
                登录
              </button>
              <button
                type="button"
                className={`flex-1 rounded-lg py-2 text-sm font-medium transition-colors ${
                  mode === "register" ? "bg-primary/10 text-primary" : "text-muted-foreground"
                }`}
                onClick={() => {
                  setMode("register");
                  setError(null);
                }}
              >
                注册
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="relative">
                <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="用户名"
                  className="pl-10"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  minLength={3}
                  maxLength={20}
                />
              </div>

              {mode === "register" && (
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    type="email"
                    placeholder="邮箱（选填）"
                    className="pl-10"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              )}

              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="password"
                  placeholder="密码"
                  className="pl-10"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                />
              </div>

              {mode === "register" && (
                <p className="text-xs text-muted-foreground">
                  密码至少8位，且需包含大写字母、小写字母、数字、特殊字符中的至少3种
                </p>
              )}

              {error && (
                <div className="flex items-start gap-2 rounded-xl border border-danger/20 bg-danger/10 p-3 text-sm text-danger">
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting ? "处理中..." : mode === "login" ? "登录" : "注册"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
