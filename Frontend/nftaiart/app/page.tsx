"use client";

import { useState } from "react";
import axios from "axios";
import PromptForm from "@/components/PromptForm";

type GenerateResponse = {
  image_url: string;
  metadata_url: string;
};

export default function Home() {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [metadataUrl, setMetadataUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async (prompt: string) => {
    try {
      setLoading(true);
      setError(null);
      setImageUrl(null);
      setMetadataUrl(null);

      const res = await axios.post<GenerateResponse>(
        "http://localhost:8000/generate",
        { prompt }
      );

      setImageUrl(res.data.image_url);
      setMetadataUrl(res.data.metadata_url);
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-black text-white p-8">
      <h1 className="text-4xl font-bold mb-6">🧠 AI NFT Art Generator</h1>
      <PromptForm onSubmit={handleGenerate} />

      {loading && <p className="mt-4 text-yellow-400">Generating image...</p>}
      {error && <p className="mt-4 text-red-500">{error}</p>}

      {imageUrl && (
        <div className="mt-8">
          <img src={imageUrl} alt="Generated AI Art" className="rounded-lg shadow-lg" />
          <a
            href={metadataUrl!}
            target="_blank"
            rel="noopener noreferrer"
            className="block mt-2 text-blue-400 underline"
          >
            View Metadata on IPFS
          </a>
        </div>
      )}
    </main>
  );
}
