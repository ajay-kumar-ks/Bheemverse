import { useEffect, useState } from 'react'
import api from '../../services/api'

function CommentItem({ comment, depth, onReply }) {
  const [replyOpen, setReplyOpen] = useState(false)
  const [replyText, setReplyText] = useState('')
  const [posting, setPosting] = useState(false)
  const marginClass = depth > 0 ? 'ml-6 border-l border-slate-200 pl-4' : ''

  const submitReply = async (event) => {
    event.preventDefault()
    if (!replyText.trim()) return
    setPosting(true)
    await onReply(comment.id, replyText.trim())
    setReplyText('')
    setReplyOpen(false)
    setPosting(false)
  }

  return (
    <div className={`rounded-xl bg-white p-4 ${marginClass}`}>
      <p className="text-xs text-slate-500">User #{comment.user_id}</p>
      <p className="mt-1 text-sm text-slate-800">
        {comment.is_flagged ? <span className="italic text-slate-400">Comment hidden</span> : comment.content}
      </p>
      <button
        type="button"
        className="mt-2 text-xs font-medium text-indigo-600 hover:text-indigo-700"
        onClick={() => setReplyOpen((v) => !v)}
      >
        {replyOpen ? 'Cancel' : 'Reply'}
      </button>

      {replyOpen && (
        <form onSubmit={submitReply} className="mt-3 space-y-2">
          <textarea
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            rows={2}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            placeholder="Write a reply..."
            required
          />
          <button
            type="submit"
            disabled={posting}
            className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-60"
          >
            {posting ? 'Posting...' : 'Post reply'}
          </button>
        </form>
      )}

      {!!comment.replies?.length && (
        <div className="mt-3 space-y-3">
          {comment.replies.map((reply) => (
            <CommentItem key={reply.id} comment={reply} depth={depth + 1} onReply={onReply} />
          ))}
        </div>
      )}
    </div>
  )
}

export default function CommentSection({ questionId }) {
  const [comments, setComments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [content, setContent] = useState('')
  const [posting, setPosting] = useState(false)

  const loadComments = async () => {
    setLoading(true)
    setError('')
    try {
      const { data } = await api.get(`/questions/${questionId}/comments`)
      setComments(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load comments.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadComments()
  }, [questionId])

  const submitComment = async (event) => {
    event.preventDefault()
    if (!content.trim()) return
    setPosting(true)
    try {
      await api.post(`/questions/${questionId}/comments`, { content: content.trim() })
      setContent('')
      await loadComments()
    } finally {
      setPosting(false)
    }
  }

  const submitReply = async (parentId, replyContent) => {
    await api.post(`/questions/${questionId}/comments/${parentId}/reply`, {
      content: replyContent,
    })
    await loadComments()
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
      <h3 className="text-lg font-semibold text-slate-900">Comments</h3>
      <form onSubmit={submitComment} className="mt-3 space-y-3">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          rows={3}
          placeholder="Add a comment..."
          required
        />
        <button
          type="submit"
          disabled={posting}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60"
        >
          {posting ? 'Posting...' : 'Post comment'}
        </button>
      </form>

      {loading ? <p className="mt-4 text-sm text-slate-500">Loading comments...</p> : null}
      {error ? <p className="mt-4 text-sm text-rose-600">{error}</p> : null}

      {!loading && !comments.length ? (
        <p className="mt-4 text-sm text-slate-500">No comments yet.</p>
      ) : (
        <div className="mt-4 space-y-3">
          {comments.map((comment) => (
            <CommentItem key={comment.id} comment={comment} depth={0} onReply={submitReply} />
          ))}
        </div>
      )}
    </section>
  )
}
