import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getProductHistory, PricePoint } from '../services/products';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function ProductDetail() {
  const { productId } = useParams<{ productId: string }>();
  const [history, setHistory] = useState<PricePoint[]>([]);
  const [prediction, setPrediction] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (productId) {
      getProductHistory(productId)
        .then(res => setHistory(res.data))
        .catch(console.error)
        .finally(() => setLoading(false));

      // chamada para previsão
      axios.get(`http://localhost:8001/predict/${productId}`)
        .then(res => setPrediction(res.data.predictions.map((p: any) => ({
          data: new Date(p.ds).toLocaleDateString(),
          previsão: p.yhat,
        }))))
        .catch(() => console.log("Previsão indisponível"));
    }
  }, [productId]);

  if (loading) return <div>Carregando gráfico...</div>;

  // dados históricos
  const historyData = history
    .filter(p => p.price != null)
    .map(p => ({
      data: new Date(p.collected_at).toLocaleDateString(),
      preço: p.price,
    }));

  // combinar histórico + previsão
  const chartData = [...historyData, ...prediction];

  return (
    <div style={{ padding: 20 }}>
      <h2>Histórico de Preços</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="data" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="preço" stroke="#8884d8" strokeWidth={2} />
          {prediction.length > 0 && (
            <Line type="monotone" dataKey="previsão" stroke="#ff7300" strokeDasharray="5 5" />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ProductDetail;
