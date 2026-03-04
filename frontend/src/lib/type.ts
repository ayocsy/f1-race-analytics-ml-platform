export type PredictRequest = {
  season: number;
  round: number;
  driver_a: string;
  driver_b: string;
};

export type PredictResponse = {
  probability_win: number;
  prediction: number;
  features_used: Record<string, number>;
};

export type OptionsResponse = {
  seasons: number[];
  rounds_by_season: Record<string, number[]>;
  drivers_by_season: Record<string, string[]>;
};

export type MetadataResponse = {
  model_type: string;
  features: string[];
  task: string;
  options: OptionsResponse;
};

export type SeasonPredictionRow = {
  season: number;
  round: number;
  event_name: string;
  event_date: string;
  constructor_id: string;
  driver_a: string;
  driver_b: string;
  probability_driver_a_win: number;
  prediction: number;
  predicted_winner: string;
  quali_pos_diff: number;
  h2h_win_rate_last_10: number;
};

export type SeasonPredictionsResponse = {
  season: number;
  assumptions: {
    quali_pos_diff: number;
    note: string;
  };
  count: number;
  predictions: SeasonPredictionRow[];
};

export type Options2026Response = {
  season: number;
  constructors: string[];
  drivers_by_constructor: Record<string, string[]>;
  rounds: {
    round: number;
    event_name: string;
    event_date: string;
  }[];
};

export type ManualPredictRequest = {
  season: number;
  round: number;
  driver_a: string;
  driver_b: string;
  quali_pos_a: number;
  quali_pos_b: number;
};
