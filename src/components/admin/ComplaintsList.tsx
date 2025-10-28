import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';

interface Complaint {
  id: number;
  chat_id: number;
  reason: string;
  created_at: string;
  status: string;
}

interface ComplaintsListProps {
  complaints: Complaint[];
}

export default function ComplaintsList({ complaints }: ComplaintsListProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20">Ожидает</Badge>;
      case 'resolved':
        return <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">Решено</Badge>;
      case 'rejected':
        return <Badge variant="outline" className="bg-red-500/10 text-red-500 border-red-500/20">Отклонено</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-3">
      {complaints.length === 0 ? (
        <Card className="p-8 text-center">
          <Icon name="CheckCircle2" size={48} className="text-green-500 mx-auto mb-3 opacity-50" />
          <p className="text-muted-foreground">Нет жалоб</p>
        </Card>
      ) : (
        complaints.map((complaint) => (
          <Card key={complaint.id} className="p-4 hover:bg-accent/5 transition-colors">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4 flex-1">
                <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center flex-shrink-0">
                  <Icon name="Flag" size={20} className="text-red-500" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="secondary" className="font-mono">
                      Чат #{complaint.chat_id}
                    </Badge>
                    {getStatusBadge(complaint.status)}
                  </div>
                  <p className="text-sm mb-2">{complaint.reason}</p>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Icon name="Calendar" size={12} />
                    {formatDate(complaint.created_at)}
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ))
      )}
    </div>
  );
}
