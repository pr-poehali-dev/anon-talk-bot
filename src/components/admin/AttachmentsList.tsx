import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import Icon from '@/components/ui/icon';

interface Attachment {
  id: number;
  chat_id: number;
  photo_url: string;
  sent_at: string;
  sender_gender: string;
}

interface AttachmentsListProps {
  attachments: Attachment[];
}

export default function AttachmentsList({ attachments }: AttachmentsListProps) {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'только что';
    if (diffMins < 60) return `${diffMins} мин назад`;
    if (diffHours < 24) return `${diffHours} ч назад`;
    if (diffDays === 1) return 'вчера';
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
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
          <CardTitle className="flex items-center gap-2">
            <Icon name="Image" size={24} />
            Вложения ({attachments.length})
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
