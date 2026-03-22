import { useState } from "react";

function App() {
  const [resultado, setResultado] = useState(null);

  const simular = async () => {
    try {
      const response = await fetch(
        "https://redesigned-robot-q7g95947vrr5crxx-8000.app.github.dev/simular",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            credito: {
              tipo: "uva",
              monto: 100000000,
              tna: 0.06,
              plazo_meses: 240,
              cftea: 0.08,
              usar_cvs: true
            },
            inversion: {
              tipo: "cer",
              capital_inicial: 5000000,
              aporte_mensual: 100000,
              tasa_anual: 0.02
            },
            macro: {
              inflacion_mensual: 0.04,
              devaluacion_mensual: 0.05
            },
            montecarlo: true
          })
        }
      );

      const data = await response.json();
      console.log("RESULTADO:", data);
      setResultado(data);

    } catch (error) {
      console.error("ERROR:", error);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Simulador Hipotecario</h1>

      <button onClick={simular}>
        Simular
      </button>

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