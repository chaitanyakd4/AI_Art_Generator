interface MintStatusProps {
  status: 'idle' | 'minting' | 'success' | 'error';
  imageUrl: string | null;
  transactionHash: string | null;
}

export default function MintStatus({ status, imageUrl, transactionHash }: MintStatusProps) {
  return (
    <div className="mt-8 w-full max-w-xl">
      {status === 'minting' && (
        <div className="bg-yellow-50 p-4 rounded-md border border-yellow-200">
          <p className="text-center text-yellow-700">
            <span className="inline-block animate-pulse mr-2">⏳</span>
            Generating your artwork and minting as an NFT...
          </p>
        </div>
      )}
      
      {status === 'error' && (
        <div className="bg-red-50 p-4 rounded-md border border-red-200">
          <p className="text-center text-red-700">
            <span className="mr-2">❌</span>
            Failed to mint NFT. Please try again.
          </p>
        </div>
      )}
      
      {status === 'success' && (
        <div className="bg-green-50 p-4 rounded-md border border-green-200">
          <div className="text-center mb-4">
            <p className="text-green-700 font-medium text-lg">
              <span className="mr-2">✅</span>
              Successfully minted as an NFT!
            </p>
          </div>
          
          {imageUrl && (
            <div className="mt-4">
              <img
                src={imageUrl}
                alt="Generated AI Art"
                className="mx-auto rounded-md shadow-md max-h-80"
              />
            </div>
          )}
          
          {transactionHash && (
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-600">Transaction Hash:</p>
              <a
                href={`https://etherscan.io/tx/${transactionHash}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-blue-600 hover:text-blue-800 break-all"
              >
                {transactionHash}
              </a>
              <p className="mt-2 text-xs text-gray-500">
                Note: For local development chains, this transaction will not appear on Etherscan
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}