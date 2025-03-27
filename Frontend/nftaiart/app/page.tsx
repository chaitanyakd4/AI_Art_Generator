'use client'
import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'

export default function ArtGenerator() {
  const [prompt, setPrompt] = useState('')
  
  // Submit new prompt
  const submitPrompt = useMutation({
    mutationFn: async (promptText: string) => {
      const { data, error } = await supabase
        .from('prompts')
        .insert([{ prompt_text: promptText }])
        .select()
        .single()
      
      if (error) throw error
      return data
    }
  })

  // Query for completed images
const { data: images } = useQuery({
  queryKey: ['generated-images'],
  queryFn: async () => {
    const { data, error } = await supabase
      .from('generated_images')
      .select('*, prompts(prompt_text)')
      .order('created_at', { ascending: false });

    return data || [];
  },
  refetchInterval: 5000 // Poll every 5 seconds
});

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">AI Art Generator</h1>
      
      {/* Prompt Form */}
      <div className="mb-8">
        <textarea
          className="w-full p-2 border rounded"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your artwork..."
          rows={3}
        />
        <button
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
          onClick={() => submitPrompt.mutate(prompt)}
          disabled={submitPrompt.isPending}
        >
          {submitPrompt.isPending ? 'Submitting...' : 'Generate Art'}
        </button>
      </div>

      {/* Status Display */}
      {submitPrompt.isSuccess && (
        <div className="mb-4 p-2 bg-blue-100 text-blue-800 rounded">
          Processing your prompt: "{submitPrompt.data.prompt_text}"
        </div>
      )}

      {/* Generated Images Gallery */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {images?.map((image) => (
          <div key={image.id} className="border rounded overflow-hidden">
            <img 
              src={image.image_url} 
              alt={image.prompts?.prompt_text || 'Generated art'}
              className="w-full h-48 object-cover"
            />
            <div className="p-2">
              <p className="text-sm">{image.prompts?.prompt_text}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 