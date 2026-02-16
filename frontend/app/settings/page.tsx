"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Settings,
  Save,
  Database,
  Bell,
  Shield,
  Palette,
  Key,
} from "lucide-react";

export default function SettingsPage() {
  const [saving, setSaving] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [dataSource, setDataSource] = useState("tushare");
  const [notifications, setNotifications] = useState(true);

  const handleSave = () => {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      alert("设置已保存！");
    }, 1000);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold">设置</h1>
          <p className="text-muted-foreground mt-1">配置您的量化研究平台</p>
        </div>
        <Button onClick={handleSave} disabled={saving}>
          <Save className={`h-4 w-4 mr-2 ${saving ? 'animate-spin' : ''}`} />
          {saving ? '保存中...' : '保存设置'}
        </Button>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <Key className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle className="text-lg">API 密钥</CardTitle>
                <CardDescription>配置数据源的 API 密钥</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Tushare API Key</label>
              <Input
                type="password"
                placeholder="输入您的 Tushare API Key"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">数据源</label>
              <select
                className="w-full h-10 px-3 rounded-md border border-white/10 bg-white/5 text-foreground"
                value={dataSource}
                onChange={(e) => setDataSource(e.target.value)}
              >
                <option value="tushare">Tushare</option>
                <option value="akshare">AkShare</option>
                <option value="yfinance">Yahoo Finance</option>
              </select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-chart-2/10 flex items-center justify-center">
                <Database className="h-5 w-5 text-chart-2" />
              </div>
              <div>
                <CardTitle className="text-lg">数据设置</CardTitle>
                <CardDescription>配置数据抓取和存储选项</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">自动更新数据</p>
                <p className="text-sm text-muted-foreground">每日自动抓取最新行情数据</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">缓存历史数据</p>
                <p className="text-sm text-muted-foreground">缓存历史数据以提高性能</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-success/10 flex items-center justify-center">
                <Bell className="h-5 w-5 text-success" />
              </div>
              <div>
                <CardTitle className="text-lg">通知设置</CardTitle>
                <CardDescription>配置通知和提醒选项</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">启用通知</p>
                <p className="text-sm text-muted-foreground">接收市场异动和评分更新通知</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={notifications}
                  onChange={(e) => setNotifications(e.target.checked)}
                />
                <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>
            {notifications && (
              <div className="pl-4 border-l-2 border-white/10 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-sm">AI 评分更新</p>
                    <p className="text-xs text-muted-foreground">股票评分发生重大变化时</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-9 h-5 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-sm">日报生成</p>
                    <p className="text-xs text-muted-foreground">每日报告生成完成时</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-9 h-5 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-warning/10 flex items-center justify-center">
                <Shield className="h-5 w-5 text-warning" />
              </div>
              <div>
                <CardTitle className="text-lg">安全设置</CardTitle>
                <CardDescription>配置账户和数据安全选项</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Button variant="outline" className="w-full justify-start">
                <Key className="h-4 w-4 mr-2" />
                修改密码
              </Button>
            </div>
            <div>
              <Button variant="outline" className="w-full justify-start">
                <Database className="h-4 w-4 mr-2" />
                导出数据
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
