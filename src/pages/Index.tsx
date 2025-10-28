import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import Icon from '@/components/ui/icon';
import { Progress } from '@/components/ui/progress';
import LoginForm from '@/components/LoginForm';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const COLORS = ['#9b87f5', '#0EA5E9', '#D946EF', '#F97316'];
const API_URL = 'https://functions.poehali.dev/3d80763a-6e9c-47e8-ad39-f66f686907a6';
const AUTH_API_URL = 'https://functions.poehali.dev/7c36ba9c-1436-4f94-ac57-6e4d16640f39';

interface Stats {
  active_users: number;
  active_chats: number;
  searching_users: number;
  pending_complaints: number;
  gender_distribution: {
    male: number;
    female: number;
  };
  hourly_stats: Array<{ hour: number; users: number; chats: number }>;
  avg_chat_duration_minutes: number;
  total_messages_today: number;
}

interface Chat {
  id: number;
  user1_gender: string;
  user2_gender: string;
  message_count: number;
  duration_minutes: number;
}

interface Complaint {
  id: number;
  chat_id: number;
  reason: string;
  created_at: string;
  status: string;
}

export default function Index() {
  const [activeTab, setActiveTab] = useState('stats');
  const [stats, setStats] = useState<Stats | null>(null);
  const [chats, setChats] = useState<Chat[]>([]);
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [authChecking, setAuthChecking] = useState(true);

  const verifySession = async (token: string) => {
    try {
      const response = await fetch(AUTH_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'verify',
          session_token: token
        })
      });
      const data = await response.json();
      return data.valid === true;
    } catch {
      return false;
    }
  };

  const handleLogout = async () => {
    if (sessionToken) {
      await fetch(AUTH_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'logout',
          session_token: sessionToken
        })
      });
    }
    localStorage.removeItem('admin_session');
    setIsAuthenticated(false);
    setSessionToken(null);
  };

  const handleLoginSuccess = (token: string) => {
    setSessionToken(token);
    setIsAuthenticated(true);
  };

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('admin_session');
      if (token) {
        const valid = await verifySession(token);
        if (valid) {
          setSessionToken(token);
          setIsAuthenticated(true);
        } else {
          localStorage.removeItem('admin_session');
        }
      }
      setAuthChecking(false);
    };
    checkAuth();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}?endpoint=stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchChats = async () => {
    try {
      const response = await fetch(`${API_URL}?endpoint=chats`);
      const data = await response.json();
      setChats(data.chats || []);
    } catch (error) {
      console.error('Failed to fetch chats:', error);
    }
  };

  const fetchComplaints = async () => {
    try {
      const response = await fetch(`${API_URL}?endpoint=complaints`);
      const data = await response.json();
      setComplaints(data.complaints || []);
    } catch (error) {
      console.error('Failed to fetch complaints:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchStats(), fetchChats(), fetchComplaints()]);
      setLoading(false);
    };
    
    loadData();
  }, []);

  const handleRefresh = async () => {
    setLoading(true);
    await Promise.all([fetchStats(), fetchChats(), fetchComplaints()]);
    setLoading(false);
  };

  const genderData = stats?.gender_distribution ? [
    { name: 'Мужчины', value: stats.gender_distribution.male || 0 },
    { name: 'Женщины', value: stats.gender_distribution.female || 0 },
  ] : [];

  const chartData = stats?.hourly_stats?.map(item => ({
    time: `${String(item.hour).padStart(2, '0')}:00`,
    users: item.users,
    chats: item.chats,
  })) || [];

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = Math.floor(minutes % 60);
    return `${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}`;
  };

  const formatGender = (g: string) => {
    return g === 'male' ? 'М' : 'Ж';
  };

  if (authChecking) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Icon name="Loader2" size={48} className="text-primary animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Проверка доступа...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginForm onSuccess={handleLoginSuccess} />;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Icon name="Loader2" size={48} className="text-primary animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Загрузка данных...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <Icon name="MessageSquare" size={24} className="text-white" />
              </div>
              Анонимный Чат-Бот
            </h1>
            <p className="text-muted-foreground mt-1">Панель администратора</p>
          </div>
          <div className="flex items-center gap-3">
            <Button onClick={handleRefresh} variant="outline" size="lg" disabled={loading}>
              <Icon name={loading ? "Loader2" : "RefreshCw"} size={18} className={`mr-2 ${loading ? 'animate-spin' : ''}`} />
              Обновить
            </Button>
            <Button onClick={handleLogout} variant="outline" size="lg">
              <Icon name="LogOut" size={18} className="mr-2" />
              Выйти
            </Button>
            <Badge variant="outline" className="px-4 py-2 text-lg font-mono">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse-slow inline-block mr-2" />
              Онлайн
            </Badge>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-6 gradient-border hover:scale-105 transition-transform cursor-pointer">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Активных пользователей</p>
                <p className="text-3xl font-bold font-mono mt-2">{stats?.active_users || 0}</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-primary/20 flex items-center justify-center">
                <Icon name="Users" size={24} className="text-primary" />
              </div>
            </div>
          </Card>

          <Card className="p-6 gradient-border hover:scale-105 transition-transform cursor-pointer">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Активных диалогов</p>
                <p className="text-3xl font-bold font-mono mt-2">{stats?.active_chats || 0}</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-secondary/20 flex items-center justify-center">
                <Icon name="MessageCircle" size={24} className="text-secondary" />
              </div>
            </div>
          </Card>

          <Card className="p-6 gradient-border hover:scale-105 transition-transform cursor-pointer">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">В поиске</p>
                <p className="text-3xl font-bold font-mono mt-2">{stats?.searching_users || 0}</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-yellow-500/20 flex items-center justify-center">
                <Icon name="Search" size={24} className="text-yellow-500" />
              </div>
            </div>
          </Card>

          <Card className="p-6 gradient-border hover:scale-105 transition-transform cursor-pointer">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Жалобы</p>
                <p className="text-3xl font-bold font-mono mt-2">{stats?.pending_complaints || 0}</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-red-500/20 flex items-center justify-center">
                <Icon name="AlertTriangle" size={24} className="text-red-500" />
              </div>
            </div>
          </Card>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 h-14">
            <TabsTrigger value="stats" className="text-base">
              <Icon name="BarChart3" size={18} className="mr-2" />
              Статистика
            </TabsTrigger>
            <TabsTrigger value="chats" className="text-base">
              <Icon name="MessageSquare" size={18} className="mr-2" />
              Активные чаты
            </TabsTrigger>
            <TabsTrigger value="complaints" className="text-base">
              <Icon name="Flag" size={18} className="mr-2" />
              Жалобы
            </TabsTrigger>
          </TabsList>

          <TabsContent value="stats" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="p-6 lg:col-span-2">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Icon name="TrendingUp" size={20} />
                  Активность за сутки
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#9b87f5" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#9b87f5" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorChats" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#0EA5E9" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#0EA5E9" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                    <XAxis dataKey="time" stroke="#888" />
                    <YAxis stroke="#888" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                      labelStyle={{ color: '#fff' }}
                    />
                    <Area
                      type="monotone"
                      dataKey="users"
                      stroke="#9b87f5"
                      fillOpacity={1}
                      fill="url(#colorUsers)"
                      name="Пользователи"
                    />
                    <Area
                      type="monotone"
                      dataKey="chats"
                      stroke="#0EA5E9"
                      fillOpacity={1}
                      fill="url(#colorChats)"
                      name="Диалоги"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Icon name="PieChart" size={20} />
                  Распределение по полу
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={genderData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {genderData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
                    <Icon name="Clock" size={20} className="text-primary" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Средняя длительность</p>
                    <p className="text-2xl font-bold font-mono">
                      {formatDuration(stats?.avg_chat_duration_minutes || 0)}
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-secondary/20 flex items-center justify-center">
                    <Icon name="MessageSquare" size={20} className="text-secondary" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Сообщений за сутки</p>
                    <p className="text-2xl font-bold font-mono">{stats?.total_messages_today || 0}</p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                    <Icon name="Activity" size={20} className="text-green-500" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Успешных матчей</p>
                    <p className="text-2xl font-bold font-mono">{chats.length}</p>
                  </div>
                </div>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="chats" className="space-y-4">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Icon name="MessageCircle" size={20} />
                  Активные диалоги ({chats.length})
                </h3>
              </div>

              <div className="space-y-3">
                {chats.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">Нет активных диалогов</p>
                ) : (
                  chats.map((chat) => (
                    <div
                      key={chat.id}
                      className="flex items-center justify-between p-4 rounded-lg bg-card/50 border border-border hover:bg-card transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <Badge variant="outline" className="font-mono">
                          #{chat.id}
                        </Badge>
                        <div className="flex items-center gap-2">
                          <Icon name="Users" size={16} className="text-muted-foreground" />
                          <span className="font-mono">
                            {formatGender(chat.user1_gender)} ↔ {formatGender(chat.user2_gender)}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-6 text-sm text-muted-foreground">
                        <div className="flex items-center gap-2">
                          <Icon name="Clock" size={14} />
                          <span className="font-mono">{formatDuration(chat.duration_minutes)}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Icon name="MessageSquare" size={14} />
                          <span className="font-mono">{chat.message_count}</span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="complaints" className="space-y-4">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Icon name="AlertTriangle" size={20} />
                  Жалобы ({complaints.filter(c => c.status === 'pending').length})
                </h3>
              </div>

              <div className="space-y-3">
                {complaints.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">Нет жалоб</p>
                ) : (
                  complaints.map((complaint) => (
                    <div
                      key={complaint.id}
                      className="flex items-center justify-between p-4 rounded-lg bg-card/50 border border-border"
                    >
                      <div className="flex items-center gap-4">
                        <Badge variant="outline" className="font-mono">
                          #{complaint.id}
                        </Badge>
                        <div>
                          <p className="font-medium">{complaint.reason}</p>
                          <p className="text-sm text-muted-foreground">
                            Чат #{complaint.chat_id} • {new Date(complaint.created_at).toLocaleString('ru-RU')}
                          </p>
                        </div>
                      </div>
                      <Badge variant={complaint.status === 'pending' ? 'destructive' : 'secondary'}>
                        {complaint.status === 'pending' ? 'Новая' : 'Рассмотрена'}
                      </Badge>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}