import { useState } from "react";

function App() {

  const [form, setForm] = useState({
    monto: 100000000,
    tasa: 0.06,
    plazo: 240,
    capital: 5000000,
    aporte: 100000,
    inflacion: 0.04,
    devaluacion: 0.05
  });

  const [resultado, setResultado] = useState(null);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: parseFloat(e.target.value)
    });
  };

  const simular = async () => {
    try {
      const response = await fetch("https://redesigned-robot-q7g95947vrr5crxx-8000.app.github.dev/simular", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            credito: {
              tipo: "uva",
              monto: form.monto,
              tna: form.tasa,
              plazo_meses: form.plazo,
              cftea: 0.08,
              usar_cvs: true
            },
            inversion: {
              tipo: "cer",
              capital_inicial: form.capital,
              aporte_mensual: form.aporte,
              tasa_anual: 0.02
            },
            macro: {
              inflacion_mensual: form.inflacion,
              devaluacion_mensual: form.devaluacion
            },
            montecarlo: false
          })
        }
      );

      const data = await response.json();
      setResultado(data);

    } catch (error) {
      console.error("ERROR:", error);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Simulador Hipotecario</h1>

      <h2>Datos del crédito</h2>

      <input name="monto" value={form.monto} onChange={handleChange} />
      <input name="tasa" value={form.tasa} onChange={handleChange} />
      <input name="plazo" value={form.plazo} onChange={handleChange} />

      <h2>Inversión</h2>

      <input name="capital" value={form.capital} onChange={handleChange} />
      <input name="aporte" value={form.aporte} onChange={handleChange} />

      <h2>Macro</h2>

      <input name="inflacion" value={form.inflacion} onChange={handleChange} />
      <input name="devaluacion" value={form.devaluacion} onChange={handleChange} />

      <br /><br />

      <button onClick={simular}>Simular</button>

      {resultado && (
        <div>
          <h2>Resultado</h2>
          <pre>
            {JSON.stringify(resultado.resultado.slice(0, 5), null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App;