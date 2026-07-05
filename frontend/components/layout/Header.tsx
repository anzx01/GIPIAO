"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Bell, LogOut, Search, User } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/lib/auth-context";

export function Header() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [searchCode, setSearchCode] = useState("");

  const handleLogout = () => {
    logout();
    router.replace("/login");
  };

  const handleSearch = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && searchCode.trim()) {
      const code = searchCode.trim();
      const formattedCode = code.includes('.') ? code : code + '.SH';
      router.push(`/stocks?code=${formattedCode}`);
    }
  };

  const handleSearchClick = () => {
    if (searchCode.trim()) {
      const code = searchCode.trim();
      const formattedCode = code.includes('.') ? code : code + '.SH';
      router.push(`/stocks?code=${formattedCode}`);
    }
  };

  return (
    <header className="flex h-16 items-center justify-between border-b border-white/5 bg-card/30 backdrop-blur-xl px-6">
      <div className="flex items-center gap-4 flex-1 max-w-md">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground cursor-pointer" onClick={handleSearchClick} />
          <Input
            type="search"
            placeholder="搜索股票代码、名称..."
            className="w-full bg-white/5 border-white/10 pl-10 focus:bg-white/10 transition-colors"
            value={searchCode}
            onChange={(e) => setSearchCode(e.target.value)}
            onKeyDown={handleSearch}
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button className="relative p-2 rounded-xl hover:bg-white/5 transition-colors">
          <Bell className="h-5 w-5 text-muted-foreground" />
          <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-primary animate-pulse" />
        </button>
        
        <div className="flex items-center gap-3 pl-4 border-l border-white/10">
          <div className="text-right">
            <p className="text-sm font-medium">{user?.username || "未登录"}</p>
            <p className="text-xs text-muted-foreground">{user?.is_admin ? "Admin" : "Account"}</p>
          </div>
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary/20 to-purple-500/20 flex items-center justify-center border border-white/10">
            <User className="h-5 w-5 text-primary" />
          </div>
          <button
            className="p-2 rounded-xl hover:bg-white/5 transition-colors"
            onClick={handleLogout}
            title="退出登录"
          >
            <LogOut className="h-4 w-4 text-muted-foreground" />
          </button>
        </div>
      </div>
    </header>
  );
}
