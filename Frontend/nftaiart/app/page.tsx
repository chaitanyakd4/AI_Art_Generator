"use client";
import { useState } from "react";
import { createClient } from "@supabase/supabase-js";
import PromptStatus from "../components/PromptStatus";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_KEY!
);

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [status, setStatus] = useState<string | null>(null);

  const handleGenerate = async () => {
    setStatus("Processing...");
    const { data, error } = await supabase
      .from("nft_prompts")
      .insert([{ prompt_text: prompt, status: "pending", created_at: new Date().toISOString() }]);

    if (error) {
      console.error("Error submitting prompt:", error.message);
      setStatus("Failed to submit prompt.");
      return;
    }

    setStatus("Submitted! Waiting for completion...");
  };

  return (
    <div className="text-center">
      <h1 className="text-3xl font-bold">AI NFT Generator</h1>
      <textarea
        className="mt-4 w-full p-2 text-black"
        placeholder="Enter your NFT prompt..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />
      <button
        className="bg-blue-500 px-4 py-2 mt-2 rounded hover:bg-blue-600"
        onClick={handleGenerate}
      >
        Generate NFT
      </button>
      {status && <PromptStatus status={status} />}
    </div>
  );
}
