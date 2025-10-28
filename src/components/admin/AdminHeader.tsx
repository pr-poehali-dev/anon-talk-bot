import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import Icon from '@/components/ui/icon';

interface AdminHeaderProps {
  loading: boolean;
  onRefresh: () => void;
  onLogout: () => void;
}

export default function AdminHeader({ loading, onRefresh, onLogout }: AdminHeaderProps) {
  return (
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
        <Button onClick={onRefresh} variant="outline" size="lg" disabled={loading}>
          <Icon name={loading ? "Loader2" : "RefreshCw"} size={18} className={`mr-2 ${loading ? 'animate-spin' : ''}`} />
          Обновить
        </Button>
        <Button onClick={onLogout} variant="outline" size="lg">
          <Icon name="LogOut" size={18} className="mr-2" />
          Выйти
        </Button>
        <Badge variant="outline" className="px-4 py-2 text-lg font-mono">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse-slow inline-block mr-2" />
          Онлайн
        </Badge>
      </div>
    </header>
  );
}
