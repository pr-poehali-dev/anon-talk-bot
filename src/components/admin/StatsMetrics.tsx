import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import Icon from '@/components/ui/icon';

interface Stats {
  avg_chat_duration_minutes: number;
  total_messages_today: number;
  active_users: number;
  active_chats: number;
}

interface StatsMetricsProps {
  stats: Stats | null;
  formatDuration: (minutes: number) => string;
}

export default function StatsMetrics({ stats, formatDuration }: StatsMetricsProps) {
  const chatEfficiency = stats ? Math.min((stats.active_chats / Math.max(stats.active_users, 1)) * 100, 100) : 0;
  const avgMessagesPerChat = stats && stats.active_chats > 0 
    ? Math.round(stats.total_messages_today / stats.active_chats) 
    : 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
            <Icon name="Clock" size={20} className="text-primary" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Средняя длительность</p>
            <p className="text-xl font-bold font-mono">{formatDuration(stats?.avg_chat_duration_minutes || 0)}</p>
          </div>
        </div>
        <Progress value={Math.min((stats?.avg_chat_duration_minutes || 0) / 60 * 100, 100)} className="h-2" />
      </Card>

      <Card className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-secondary/20 flex items-center justify-center">
            <Icon name="MessageSquare" size={20} className="text-secondary" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Сообщений за сегодня</p>
            <p className="text-xl font-bold font-mono">{stats?.total_messages_today || 0}</p>
          </div>
        </div>
        <Progress value={Math.min((stats?.total_messages_today || 0) / 1000 * 100, 100)} className="h-2" />
      </Card>

      <Card className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
            <Icon name="TrendingUp" size={20} className="text-green-500" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Эффективность матчинга</p>
            <p className="text-xl font-bold font-mono">{chatEfficiency.toFixed(0)}%</p>
          </div>
        </div>
        <Progress value={chatEfficiency} className="h-2" />
      </Card>
    </div>
  );
}
