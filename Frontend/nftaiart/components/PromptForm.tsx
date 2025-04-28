import { useState } from "react";

interface PromptFormProps {
  onSubmit: (prompt: string) => void;
  isWalletConnected: boolean;
}

export default function PromptForm({ onSubmit, isWalletConnected }: PromptFormProps) {
  const [prompt, setPrompt] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    
    try {
      setIsSubmitting(true);
      // Pass the prompt up to the parent component
      onSubmit(prompt.trim());
    } catch (error) {
      console.error("❌ Error submitting prompt:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your NFT artwork (e.g., 'A cosmic jellyfish floating through a nebula')"
          className="w-full p-4 pr-24 bg-white/10 backdrop-blur-sm border border-purple-500/30 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
          rows={4}
          required
          disabled={isSubmitting || !isWalletConnected}
        />
        <button
          type="submit"
          disabled={isSubmitting || !prompt.trim() || !isWalletConnected}
          className={`absolute right-3 bottom-3 px-4 py-2 rounded-md font-medium transition-all ${
            isSubmitting || !prompt.trim() || !isWalletConnected
              ? "bg-gray-600 text-gray-400 cursor-not-allowed"
              : "bg-purple-600 hover:bg-purple-700 text-white"
          }`}
        >
          {isSubmitting ? "Creating..." : "Generate"}
        </button>
      </div>
      
      {!isWalletConnected && (
        <p className="mt-2 text-yellow-400 text-sm">
          Please connect your wallet first to generate NFT art
        </p>
      )}
    </form>
  );
}