export type NFTPrompt = {
    id: number;
    prompt_text: string;
    status: "pending" | "processing" | "completed" | "failed";
    asset_url?: string;
    created_at: string;
  };
  