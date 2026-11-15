export type StageId = "detection" | "referral" | "diagnosis" | "treatment";

export interface Meta {
  schema_version?: string;
  is_example?: boolean;
  title?: string;
  disclaimer?: string;
  updated?: string;
  national_aggregation?: string;
  note?: string;
  geo_attribution?: string;
}

export interface StageDef {
  id: StageId;
  label: string;
  label_fi?: string;
  order: number;
  short?: string;
}

export interface IndicatorCatalogEntry {
  id: string;
  stage: StageId;
  label: string;
  label_fi?: string;
  unit: string;
  higher_is_better: boolean;
  decimals?: number;
  target?: number | null;
  target_source_id?: string;
  target_note?: string;
  goal?: string;
  goal3_indicator?: string | null;
}

export interface IndicatorValue {
  id: string;
  value: number | null;
  year?: number | string | null;
  source_id?: string;
  source_url?: string;
  source_table?: string;
  is_example?: boolean;
  note?: string;
  label?: string;
  unit?: string;
  stage?: StageId;
  higher_is_better?: boolean;
  target?: number | null;
  missing?: boolean;
  missing_reason?: string;
  yta_id?: string;
  data_quality?: string;
  exclude_from_ranking?: boolean;
  numerator?: number | null;
  denominator?: number | null;
  ci95_low?: number | null;
  ci95_high?: number | null;
  abs_value?: number | null;
  iqr?: number[] | null;
  men?: { value: number; ci95?: number[] } | null;
  women?: { value: number; ci95?: number[] } | null;
  measure_label?: string | null;
}

export interface Region {
  id: string;
  slug?: string;
  name: string;
  name_fi?: string;
  name_official_en?: string;
  name_official_fi?: string;
  type?: "wellbeing_services_county" | "city" | "autonomous_region";
  sotkanet_id?: number;
  include_in_national?: boolean;
  yta_id?: string;
  indicators: IndicatorValue[];
}

export interface RegionsFile {
  meta: Meta;
  stages: StageDef[];
  indicator_catalog: IndicatorCatalogEntry[];
  national: Omit<Region, "type" | "include_in_national"> & { id: string };
  regions: Region[];
}

export interface Source {
  id: string;
  title: string;
  publisher: string;
  url?: string | null;
  accessed?: string;
  year?: number | null;
  note?: string;
}

export interface SourcesFile {
  meta: Meta;
  sources: Source[];
}

export interface KeyMessageFile {
  meta: Meta;
  headline?: string;
  gap?: string;
  where_in_pathway?: string;
  what_to_do?: string;
  primary_rec_id?: string;
  spotlight_stage?: StageId;
  spotlight_indicator_id?: string;
  source_ids?: string[];
  tasan_clock_note?: string;
}

export interface Cost {
  label?: string;
  amount?: number;
  currency?: string;
  basis?: string;
  source_id?: string;
  is_example?: boolean;
}

export interface Kpi {
  name?: string;
  indicator_id?: string;
  unit?: string;
  target?: string;
  baseline?: string;
  cadence?: string;
  owner?: string;
}

export interface ExpectedEffect {
  indicator_id: string;
  direction?: "increase" | "decrease";
  delta?: number;
  unit?: string;
  horizon?: string;
  source_id?: string;
  assumptions?: string;
  is_example?: boolean;
}

export interface EffectParams {
  type?: "linear";
  applies_to_indicator: string;
  effect_at_full_coverage: number;
  max_coverage?: number;
  applicable_regions?: string[];
  region_modifiers?: Record<string, number>;
  clamp_min?: number;
  clamp_max?: number;
}

export interface Goal3Indicator {
  id: string;
  label: string;
  label_fi?: string;
  strategy_ref?: string;
  source_id?: string;
}

export interface Recommendation {
  id: string;
  title: string;
  stage?: StageId | string;
  what?: string;
  action?: string;
  why?: string;
  how?: string;
  who_implements?: string;
  owner?: string;
  cost?: Cost;
  kpi?: Kpi;
  kpis?: Kpi[];
  goal3_indicator?: string | null;
  goal3_mapping?: string;
  goal?: string;
  evidence?: string | unknown;
  evidence_source_ids?: string[];
  expected_effect?: ExpectedEffect;
  effect_params?: EffectParams;
  top3?: boolean;
  priority_rank?: number | null;
  nonpriority?: boolean;
  optional_goal2?: boolean;
  pilot_county?: string;
  data_basis?: string | unknown;
  flags?: Record<string, unknown>;
  owner_role?: string | OwnerRole | null;
  cost_range?: CostRange | null;
  stop_go?: StopGo | null;
  already_exists?: string | null;
  kpi_framing?: string | null;
  design?: string | string[] | Record<string, unknown> | null;
  target_times_caveat?: string | null;
}

export interface CostRange {
  low?: number | null;
  high?: number | null;
  currency?: string;
  period?: string;
  basis?: string[];
  lines?: unknown;
  unsourced_effort?: string[] | null;
  condition?: string;
  conditional?: boolean;
}

export interface OwnerRole {
  signer?: string;
  owner_of_delayed_patients?: string;
  data_owner?: string;
  operational_sponsor?: string;
  clinical_lead?: string;
  partners?: string[];
  by_county?: Record<string, OwnerRole | string>;
  [key: string]: unknown;
}

export interface StopGo {
  review_day?: number;
  decision_owner?: string;
  go_if_all?: string[];
  stop_or_redesign_if_any?: string[];
  week1_gate?: string | Record<string, unknown>;
  [key: string]: unknown;
}

export interface RecommendationsFile {
  meta: Meta;
  project?: string;
  top3_ids?: string[];
  lead_id?: string;
  centrepiece_id?: string;
  primary_rec_id?: string;
  display_ids?: string[];
  tasan_clock_note?: string;
  clock_note?: string;
  what_to_do?: string;
  hero_headline?: string;
  target_times_caveat?: string;
  goal3_indicators?: Goal3Indicator[];
  recommendations: Recommendation[];
}

export interface LoadReport {
  used_example: boolean;
  is_example: boolean;
  errors: string[];
  warnings: string[];
  loaded_from: Record<string, string>;
  files: Record<string, string>;
  synced_at?: string;
}

export interface GeoProperties {
  id: string;
  name_fi?: string;
  name_en?: string;
  name_sv?: string;
}

export interface GeoFeature {
  type: "Feature";
  properties: GeoProperties;
  geometry: {
    type: "Polygon" | "MultiPolygon";
    coordinates: number[][][] | number[][][][];
  };
}

export interface GeoCollection {
  type: "FeatureCollection";
  name?: string;
  attribution?: string;
  features: GeoFeature[];
}


export interface YtaModality {
  median: number;
  q1: number | null;
  q3: number | null;
  unit: string;
  year?: string;
  source_id: string;
  source_url?: string;
  source_table?: string;
  indicator?: string;
}

export interface YtaWait {
  id: string;
  name: string;
  name_fi: string;
  official_fi?: string;
  modalities: {
    surgery?: YtaModality;
    radiotherapy?: YtaModality;
    drug?: YtaModality;
  };
  source_id?: string;
}

export interface HeroHeadline {
  id: string;
  label: string;
  caveat: string;
  source_url?: string;
  source_table?: string;
  goal_link?: string;
  value?: number | number[] | null;
  unit?: string;
  national?: number;
  n?: number | string;
  N?: number;
  period?: string;
  ci_method?: string;
  regions?: Array<Record<string, unknown>>;
  age_standardised_check?: Record<string, unknown>;
  measure_label?: string;
  crude_secondary?: Record<string, unknown>;
  other_areas?: Record<string, number>;
  [key: string]: unknown;
}

export interface HeroFile {
  mode: string;
  product_name?: string;
  target_days: number;
  target_source_id?: string;
  target_times_caveat?: string;
  tasan_clock_note?: string;
  lead_id?: string;
  yta_waits: YtaWait[];
  county_yta: Record<string, string>;
  stage_coverage?: {
    source_id?: string;
    n_total?: number;
    missing_n?: number;
    missing_pct?: number;
    coverage_pct?: number;
    target_pct?: number;
  };
  key_facts?: Record<string, unknown>;
  secondary?: Record<string, unknown>;
  headlines?: HeroHeadline[];
  target_reference?: {
    value?: number;
    unit?: string;
    label?: string;
    source_url?: string;
    source_table?: string;
    caveat?: string;
  };
  excluded?: Record<string, string>;
  goal?: string;
  generated?: string;
  project?: string;
  hero_from?: string;
  people_number?: PeopleNumber;
  crude_curative?: CrudeCurative;
}

export type FactMeasureType = "published" | "computed_by_tasan" | "chart_estimate" | "no_public_data";

export interface Fact {
  id: string;
  statement_fi: string;
  statement_en: string;
  value: number | null;
  unit: string | null;
  region: string | Record<string, unknown> | null;
  years: string | null;
  pathway_stage: string | null;
  goal_link: string | null;
  source_url: string;
  source_table: string;
  measure_type: FactMeasureType;
  caveat: string;
  checks?: Array<Record<string, unknown>>;
}

export interface FactsFile {
  generated?: string;
  project?: string;
  description?: string;
  usage_rules: string[];
  measure_types?: Record<string, string>;
  n_facts?: number;
  facts: Fact[];
}

export interface PeopleNumberCounty {
  region?: string;
  code?: string;
  n?: number;
  N?: number;
  share_pct?: number;
  gap_5y?: number;
  gap_per_year?: number;
}

export interface PeopleNumber {
  value_per_year?: number;
  value_5y?: number;
  lapland_per_year?: number;
  unit?: string;
  statement_en?: string;
  statement_fi?: string;
  method?: string;
  counties?: PeopleNumberCounty[];
  period?: string;
  source_url?: string;
  source_table?: string;
  caveat?: string;
  safe_wording_en?: string;
  do_not_say?: string[];
}


export interface CrudeCurativeCounty {
  code: string;
  region?: string;
  n: number;
  N: number;
  share_pct: number;
  gap_5y: number;
  gap_per_year: number;
  below_national: boolean;
}

export interface CrudeCurative {
  national_pct: number;
  national_n: number;
  national_N: number;
  national_share?: number;
  period?: string;
  source_table?: string;
  source_url?: string;
  measure_label?: string;
  counties: CrudeCurativeCounty[];
}

export interface Dataset {
  regions: RegionsFile;
  sources: SourcesFile;
  keyMessage: KeyMessageFile;
  recs: RecommendationsFile;
  counties: GeoCollection;
  report: LoadReport;
  hero: HeroFile;
  facts: FactsFile;
}

export interface ResolvedIndicator {
  id: string;
  stage: StageId;
  label: string;
  unit: string;
  higher_is_better: boolean;
  decimals: number;
  target: number | null;
  target_source_id?: string;
  target_note?: string;
  goal?: string;
  goal3_indicator?: string | null;
  value: number | null;
  year: number | string | null;
  source_id?: string;
  is_example: boolean;
  note?: string;
  missing?: boolean;
  missing_reason?: string;
  yta_id?: string;
  data_quality?: string;
  exclude_from_ranking?: boolean;
  numerator?: number | null;
  denominator?: number | null;
  ci95_low?: number | null;
  ci95_high?: number | null;
  iqr?: number[] | null;
  men?: { value: number; ci95?: number[] } | null;
  women?: { value: number; ci95?: number[] } | null;
  measure_label?: string | null;
}
