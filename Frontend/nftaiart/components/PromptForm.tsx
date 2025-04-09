"use client";

import { useState } from "react";
import axios from "axios";

type GenerateResponse = {
  image_url: string;
  metadata_url: string;
};

type PromptFormProps = {
  onSubmit?: (prompt: string) => Promise<void>;
};

export default function PromptForm({ onSubmit }: PromptFormProps) {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [metadataUrl, setMetadataUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setImageUrl(null);
    setMetadataUrl(null);

    try {
      if (onSubmit) {
        await onSubmit(prompt); // optional external handler
        return;
      }

      const res = await axios.post<GenerateResponse>("http://localhost:8000/generate", { prompt });
      const data = res.data;
      setImageUrl(data.image_url);
      setMetadataUrl(data.metadata_url);
    } catch (err) {
      console.error(err);
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your prompt..."
          className="p-2 rounded bg-gray-800 text-white"
        />
        <button
          type="submit"
          className="bg-purple-600 hover:bg-purple-700 p-2 rounded text-white"
          disabled={loading}
        >
          {loading ? "Generating..." : "Generate Art"}
        </button>
      </form>

      {error && <p className="text-red-500 mt-4">{error}</p>}

      {imageUrl && (
        <div className="mt-6">
          <p className="text-green-400 mb-2">✅ Image generated:</p>
          <img src={imageUrl} alt="Generated Art" className="rounded shadow-lg" />
          {metadataUrl && (
            <p className="mt-2 text-sm">
              View Metadata:{" "}
              <a href={metadataUrl} target="_blank" rel="noopener noreferrer" className="underline text-blue-400">
                {metadataUrl}
              </a>
            </p>
          )}
        </div>
      )}
    </div>
  );
}
