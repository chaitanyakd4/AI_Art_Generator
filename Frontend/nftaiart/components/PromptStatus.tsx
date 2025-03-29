export default function PromptStatus() {
  return (
    <div className="text-center py-8">
      <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600 mb-4"></div>
      <h3 className="text-lg font-medium">Generating your NFT</h3>
      <p className="text-gray-500">This typically takes 30-60 seconds</p>
    </div>
  );
}