'use client'
import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'

export default function PromptStatus({ promptId }: { promptId: string }) {
  const [status, setStatus] = useState('pending')

  useEffect(() => {
    const channel = supabase
      .channel('prompt_changes')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'prompts',
          filter: `id=eq.${promptId}`
        },
        (payload) => {
          setStatus(payload.new.status)
        }
      )
      .subscribe()

    return () => { channel.unsubscribe() }
  }, [promptId])

  return (
    <div className="text-sm">
      Status: <span className="font-medium">{status}</span>
      {status === 'processing' && (
        <span className="ml-2 animate-pulse">🔄</span>
      )}
    </div>
  )
}