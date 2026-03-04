import PredictorForm from "@/components/predictorForm";

export default function Home() {
  return (
    <main className="page">
      <section className="hero">
        <h1>F1 Teammate Outcome Predictor</h1>
        <p>Select season, round, and drivers to estimate who finishes ahead.</p>
      </section>
      <PredictorForm />
    </main>
  );
}
