import { Card } from '@/components/ui/card';
import Icon from '@/components/ui/icon';

interface Stats {
  active_users: number;
  active_chats: number;
  searching_users: number;
  pending_complaints: number;
}

interface StatsCardsProps {
  stats: Stats | null;
}

export default function StatsCards({ stats }: StatsCardsProps) {
  return (
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
            <p className="text-sm text-muted-foreground">Жалоб</p>
            <p className="text-3xl font-bold font-mono mt-2">{stats?.pending_complaints || 0}</p>
          </div>
          <div className="w-12 h-12 rounded-lg bg-red-500/20 flex items-center justify-center">
            <Icon name="Flag" size={24} className="text-red-500" />
          </div>
        </div>
      </Card>
    </div>
  );
}
