import { Card } from '@/components/ui/card';
import Icon from '@/components/ui/icon';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface ChartData {
  time: string;
  users: number;
  chats: number;
}

interface ActivityChartProps {
  chartData: ChartData[];
}

export default function ActivityChart({ chartData }: ActivityChartProps) {
  return (
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
  );
}
