export type Prompt = {
    id: string
    prompt_text: string
    status: 'pending' | 'processing' | 'completed' | 'failed'
    created_at: string
    error?: string
  }
  
  export type GeneratedImage = {
    id: string
    prompt_id: string
    image_url: string
    model_used: string
    created_at: string
    prompts?: {
      prompt_text: string
    }
  }