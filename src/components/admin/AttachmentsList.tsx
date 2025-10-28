import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';

const CLEANUP_API_URL = 'https://functions.poehali.dev/44deba1f-2392-4866-9015-8df267216a6c';

interface Attachment {
  id: number;
  chat_id: number;
  photo_url: string;
  sent_at: string;
  sender_gender: string;
}

interface AttachmentsListProps {
  attachments: Attachment[];
  onCleanupComplete: () => void;
}

export default function AttachmentsList({ attachments, onCleanupComplete }: AttachmentsListProps) {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isCleaningUp, setIsCleaningUp] = useState(false);
  const { toast } = useToast();

  const handleCleanup = async () => {
    setIsCleaningUp(true);
    try {
      const response = await fetch(CLEANUP_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      
      if (response.ok) {
        toast({
          title: 'Очистка завершена',
          description: `Удалено вложений: ${data.deleted_count}`,
        });
        onCleanupComplete();
      } else {
        throw new Error(data.error || 'Ошибка очистки');
      }
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось выполнить очистку',
        variant: 'destructive',
      });
    } finally {
      setIsCleaningUp(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);

    if (diffMins < 1) return 'только что';
    if (diffMins < 60) return `${diffMins} мин назад`;
    if (diffHours < 24) return `${diffHours} ч назад`;
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
  };

  const getTimeUntilDeletion = (dateStr: string) => {
    const date = new Date(dateStr);
    const deletionTime = new Date(date.getTime() + 24 * 60 * 60 * 1000);
    const now = new Date();
    const diffMs = deletionTime.getTime() - now.getTime();
    const hoursLeft = Math.floor(diffMs / (60 * 60 * 1000));
    const minsLeft = Math.floor((diffMs % (60 * 60 * 1000)) / (60 * 1000));

    if (hoursLeft > 0) return `${hoursLeft}ч`;
    if (minsLeft > 0) return `${minsLeft}м`;
    return 'скоро';
  };

  const getGenderIcon = (gender: string) => {
    if (gender === 'male') return { icon: 'User', color: 'text-blue-500' };
    if (gender === 'female') return { icon: 'User', color: 'text-pink-500' };
    return { icon: 'User', color: 'text-gray-500' };
  };

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Icon name="Image" size={24} />
              Вложения ({attachments.length})
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-sm font-normal text-muted-foreground">
                <Icon name="Clock" size={16} />
                Автоудаление 24ч
              </div>
              <Button 
                onClick={handleCleanup} 
                disabled={isCleaningUp || attachments.length === 0}
                variant="destructive"
                size="sm"
              >
                {isCleaningUp ? (
                  <>
                    <Icon name="Loader2" size={16} className="mr-2 animate-spin" />
                    Очистка...
                  </>
                ) : (
                  <>
                    <Icon name="Trash2" size={16} className="mr-2" />
                    Очистить старые
                  </>
                )}
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {attachments.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Icon name="Image" size={48} className="mx-auto mb-4 opacity-20" />
              <p>Пока нет фото в чатах</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {attachments.map((attachment) => {
                const genderInfo = getGenderIcon(attachment.sender_gender);
                return (
                  <div
                    key={attachment.id}
                    className="group relative aspect-square rounded-lg overflow-hidden bg-muted cursor-pointer transition-transform hover:scale-105"
                    onClick={() => setSelectedImage(attachment.photo_url)}
                  >
                    <img
                      src={attachment.photo_url}
                      alt={`Фото из чата ${attachment.chat_id}`}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                    <div className="absolute top-2 right-2 bg-red-500/90 text-white text-xs px-2 py-1 rounded flex items-center gap-1">
                      <Icon name="Clock" size={12} />
                      {getTimeUntilDeletion(attachment.sent_at)}
                    </div>
                    <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-between p-2">
                      <div className="flex justify-between items-start">
                        <span className={`text-xs ${genderInfo.color}`}>
                          <Icon name={genderInfo.icon as any} size={16} />
                        </span>
                        <span className="text-xs text-white bg-black/50 px-2 py-1 rounded">
                          CH-{attachment.chat_id}
                        </span>
                      </div>
                      <span className="text-xs text-white">
                        {formatDate(attachment.sent_at)}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {selectedImage && (
        <div
          className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <button
            className="absolute top-4 right-4 text-white hover:text-gray-300 transition-colors"
            onClick={() => setSelectedImage(null)}
          >
            <Icon name="X" size={32} />
          </button>
          <img
            src={selectedImage}
            alt="Просмотр фото"
            className="max-w-full max-h-full object-contain rounded-lg"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
}