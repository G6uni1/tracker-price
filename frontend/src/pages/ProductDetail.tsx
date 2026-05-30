// frontend/src/pages/ProductDetail.tsx — CORRIGIDO
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';  // <-- import necessário
import { getProductHistory, PricePoint } from '../services/products';
import {
  LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

function ProductDetail() {
  const { productId } = useParams<{ productId: string }>();
  const [history, setHistory] = useState<PricePoint[]>([]);
  const [prediction, setPrediction] = useState<{ data: string; previsão: number }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!productId) return;

    const loadData = async () => {
      try {
        const histRes = await getProductHistory(productId);
        setHistory(histRes.data);
      } catch (err) {
        console.error('Erro ao carregar histórico:', err);
      } finally {
        setLoading(false);
      }

      try {
        const predRes = await api.get(`/predictions/${productId}`);
        const mapped = predRes.data.predictions.map((p: { ds: string; yhat: number }) => ({
          data: new Date(p.ds).toLocaleDateString('pt-BR'),
          previsão: Math.round(p.yhat * 100) / 100,
        }));
        setPrediction(mapped);
      } catch {
        console.log('Previsão indisponível');
      }
    };

    loadData();
  }, [productId]);

  if (loading) return <div>Carregando...</div>;

  const historyData = history
    .filter(p => p.price != null)
    .map(p => ({
      data: new Date(p.collected_at).toLocaleDateString('pt-BR'),
      preço: p.price,
    }));

  const chartData = [...historyData, ...prediction];

  return (
    <div style={{ padding: 20 }}>
      <h2>Histórico de Preços</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="data" />
          <YAxis />
          <Tooltip formatter={(value: number) => `R$ ${value.toFixed(2)}`} />
          <Line type="monotone" dataKey="preço" stroke="#8884d8" strokeWidth={2} dot={false} />
          {prediction.length > 0 && (
            <Line
              type="monotone"
              dataKey="previsão"
              stroke="#ff7300"
              strokeDasharray="5 5"
              dot={false}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ProductDetail;