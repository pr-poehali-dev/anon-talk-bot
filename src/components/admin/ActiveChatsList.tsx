import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';

interface Chat {
  id: number;
  user1_gender: string;
  user2_gender: string;
  message_count: number;
  duration_minutes: number;
}

interface ActiveChatsListProps {
  chats: Chat[];
  formatDuration: (minutes: number) => string;
  formatGender: (g: string) => string;
}

export default function ActiveChatsList({ chats, formatDuration, formatGender }: ActiveChatsListProps) {
  return (
    <div className="space-y-3">
      {chats.length === 0 ? (
        <Card className="p-8 text-center">
          <Icon name="MessageSquareOff" size={48} className="text-muted-foreground mx-auto mb-3 opacity-50" />
          <p className="text-muted-foreground">Нет активных диалогов</p>
        </Card>
      ) : (
        chats.map((chat) => (
          <Card key={chat.id} className="p-4 hover:bg-accent/5 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white font-mono font-bold">
                  {chat.id}
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant="outline" className="font-mono">
                      {formatGender(chat.user1_gender)} ↔ {formatGender(chat.user2_gender)}
                    </Badge>
                    <Badge variant="secondary" className="font-mono">
                      <Icon name="MessageSquare" size={12} className="mr-1" />
                      {chat.message_count}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Icon name="Clock" size={14} />
                    {formatDuration(chat.duration_minutes)}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse-slow" />
                <span className="text-xs text-muted-foreground">Активен</span>
              </div>
            </div>
          </Card>
        ))
      )}
    </div>
  );
}
