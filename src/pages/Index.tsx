import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import Icon from '@/components/ui/icon';
import { Progress } from '@/components/ui/progress';
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

const statsData = [
  { time: '00:00', users: 45, chats: 22 },
  { time: '04:00', users: 32, chats: 15 },
  { time: '08:00', users: 78, chats: 38 },
  { time: '12:00', users: 124, chats: 61 },
  { time: '16:00', users: 156, chats: 78 },
  { time: '20:00', users: 189, chats: 94 },
  { time: '23:59', users: 142, chats: 71 },
];

const genderData = [
  { name: 'Мужчины', value: 58 },
  { name: 'Женщины', value: 42 },
];

const activeChats = [
  { id: 'CH-001', duration: '12:34', gender: 'М ↔ Ж', messages: 47, status: 'active' },
  { id: 'CH-002', duration: '08:12', gender: 'Ж ↔ Ж', messages: 23, status: 'active' },
  { id: 'CH-003', duration: '25:45', gender: 'М ↔ М', messages: 89, status: 'active' },
  { id: 'CH-004', duration: '03:21', gender: 'М ↔ Ж', messages: 12, status: 'active' },
  { id: 'CH-005', duration: '15:08', gender: 'Ж ↔ Ж', messages: 56, status: 'active' },
];

const complaints = [
  { id: 'R-001', time: '14:23', reason: 'Оскорбления', status: 'pending', chatId: 'CH-089' },
  { id: 'R-002', time: '13:45', reason: 'Спам', status: 'pending', chatId: 'CH-067' },
  { id: 'R-003', time: '12:10', reason: 'Неприемлемый контент', status: 'reviewed', chatId: 'CH-034' },
];

export default function Index() {
  const [activeTab, setActiveTab] = useState('stats');

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
          <Badge variant="outline" className="px-4 py-2 text-lg font-mono">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse-slow inline-block mr-2" />
            Онлайн
          </Badge>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-6 gradient-border hover:scale-105 transition-transform cursor-pointer">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Активных пользователей</p>
                <p className="text-3xl font-bold font-mono mt-2">189</p>
                <p className="text-xs text-green-500 mt-1">+12% за час</p>
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
                <p className="text-3xl font-bold font-mono mt-2">94</p>
                <p className="text-xs text-blue-500 mt-1">+8 новых</p>
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
                <p className="text-3xl font-bold font-mono mt-2">23</p>
                <p className="text-xs text-yellow-500 mt-1">среднее: 18</p>
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
                <p className="text-3xl font-bold font-mono mt-2">2</p>
                <p className="text-xs text-red-500 mt-1">требуют действий</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-red-500/20 flex items-center justify-center">
                <Icon name="AlertTriangle" size={24} className="text-red-500" />
              </div>
            </div>
          </Card>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 h-14">
            <TabsTrigger value="stats" className="text-base">
              <Icon name="BarChart3" size={18} className="mr-2" />
              Статистика
            </TabsTrigger>
            <TabsTrigger value="chats" className="text-base">
              <Icon name="MessageSquare" size={18} className="mr-2" />
              Активные чаты
            </TabsTrigger>
            <TabsTrigger value="moderation" className="text-base">
              <Icon name="Shield" size={18} className="mr-2" />
              Модерация
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
                  <AreaChart data={statsData}>
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
                  <Icon name="Users" size={20} />
                  Распределение по полу
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={genderData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}%`}
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
                <div className="mt-4 space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded-full bg-[#9b87f5]" />
                      Мужчины
                    </span>
                    <span className="font-mono">58%</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded-full bg-[#0EA5E9]" />
                      Женщины
                    </span>
                    <span className="font-mono">42%</span>
                  </div>
                </div>
              </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Средняя продолжительность диалога</h3>
                <p className="text-4xl font-bold font-mono">18:42</p>
                <Progress value={74} className="mt-4" />
                <p className="text-sm text-muted-foreground mt-2">+15% по сравнению с вчера</p>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Сообщений за сегодня</h3>
                <p className="text-4xl font-bold font-mono">12,847</p>
                <Progress value={82} className="mt-4" />
                <p className="text-sm text-muted-foreground mt-2">Пик активности: 20:00-22:00</p>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="chats" className="space-y-4">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Icon name="Radio" size={20} className="text-green-500 animate-pulse" />
                  Активные диалоги ({activeChats.length})
                </h3>
                <Button variant="outline" size="sm">
                  <Icon name="RefreshCw" size={16} className="mr-2" />
                  Обновить
                </Button>
              </div>

              <div className="space-y-3">
                {activeChats.map((chat) => (
                  <Card
                    key={chat.id}
                    className="p-4 hover:border-primary/50 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center font-mono text-sm">
                          {chat.id}
                        </div>
                        <div>
                          <div className="flex items-center gap-3">
                            <Badge variant="outline" className="font-mono">
                              {chat.gender}
                            </Badge>
                            <span className="text-sm text-muted-foreground">
                              Длительность: <span className="font-mono">{chat.duration}</span>
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">
                            Сообщений: {chat.messages}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className="bg-green-500/20 text-green-500">Активен</Badge>
                        <Button variant="ghost" size="sm">
                          <Icon name="Eye" size={16} />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="moderation" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Icon name="Settings" size={20} />
                  Настройки системы
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 rounded-lg bg-muted/50">
                    <div>
                      <p className="font-medium">Автоматическая модерация</p>
                      <p className="text-sm text-muted-foreground">Фильтр запрещённых слов</p>
                    </div>
                    <Badge className="bg-green-500/20 text-green-500">Активна</Badge>
                  </div>

                  <div className="flex items-center justify-between p-4 rounded-lg bg-muted/50">
                    <div>
                      <p className="font-medium">Макс. длина сообщения</p>
                      <p className="text-sm text-muted-foreground">Ограничение символов</p>
                    </div>
                    <span className="font-mono text-lg">1000</span>
                  </div>

                  <div className="flex items-center justify-between p-4 rounded-lg bg-muted/50">
                    <div>
                      <p className="font-medium">Тайм-аут неактивности</p>
                      <p className="text-sm text-muted-foreground">Отключение бездействующих</p>
                    </div>
                    <span className="font-mono text-lg">10 мин</span>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Icon name="Ban" size={20} />
                  Быстрые действия
                </h3>
                <div className="space-y-3">
                  <Button variant="outline" className="w-full justify-start" size="lg">
                    <Icon name="UserX" size={18} className="mr-2" />
                    Заблокировать пользователя
                  </Button>
                  <Button variant="outline" className="w-full justify-start" size="lg">
                    <Icon name="MessageSquareOff" size={18} className="mr-2" />
                    Разорвать диалог
                  </Button>
                  <Button variant="outline" className="w-full justify-start" size="lg">
                    <Icon name="AlertCircle" size={18} className="mr-2" />
                    Отправить предупреждение
                  </Button>
                  <Button variant="outline" className="w-full justify-start" size="lg">
                    <Icon name="Archive" size={18} className="mr-2" />
                    Посмотреть архив
                  </Button>
                </div>
              </Card>
            </div>

            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Icon name="Activity" size={20} />
                Системный статус
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Загрузка процессора</p>
                  <Progress value={34} />
                  <p className="text-xs font-mono">34%</p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Использование памяти</p>
                  <Progress value={67} />
                  <p className="text-xs font-mono">67%</p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Uptime</p>
                  <p className="text-2xl font-mono">15д 7ч</p>
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="complaints" className="space-y-4">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Icon name="AlertTriangle" size={20} className="text-red-500" />
                  Жалобы пользователей
                </h3>
                <Badge variant="destructive">{complaints.filter((c) => c.status === 'pending').length} новых</Badge>
              </div>

              <div className="space-y-3">
                {complaints.map((complaint) => (
                  <Card
                    key={complaint.id}
                    className={`p-4 transition-colors ${
                      complaint.status === 'pending'
                        ? 'border-red-500/50 hover:border-red-500'
                        : 'opacity-60'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
                          <Icon name="Flag" size={20} className="text-red-500" />
                        </div>
                        <div>
                          <div className="flex items-center gap-3">
                            <span className="font-mono font-semibold">{complaint.id}</span>
                            <Badge variant="outline">{complaint.reason}</Badge>
                            <span className="text-sm text-muted-foreground">
                              Чат: {complaint.chatId}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">Время: {complaint.time}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {complaint.status === 'pending' ? (
                          <>
                            <Button size="sm" variant="destructive">
                              <Icon name="Ban" size={16} className="mr-2" />
                              Заблокировать
                            </Button>
                            <Button size="sm" variant="outline">
                              <Icon name="Eye" size={16} className="mr-2" />
                              Просмотреть
                            </Button>
                          </>
                        ) : (
                          <Badge variant="secondary">Рассмотрено</Badge>
                        )}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Статистика жалоб за неделю</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-muted/50">
                  <p className="text-sm text-muted-foreground">Всего жалоб</p>
                  <p className="text-3xl font-bold font-mono mt-2">47</p>
                </div>
                <div className="p-4 rounded-lg bg-muted/50">
                  <p className="text-sm text-muted-foreground">Обработано</p>
                  <p className="text-3xl font-bold font-mono mt-2 text-green-500">45</p>
                </div>
                <div className="p-4 rounded-lg bg-muted/50">
                  <p className="text-sm text-muted-foreground">Ожидают</p>
                  <p className="text-3xl font-bold font-mono mt-2 text-red-500">2</p>
                </div>
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
