let toastContainer: HTMLDivElement | null = null

const ensureContainer = () => {
  if (!toastContainer) {
    toastContainer = document.createElement('div')
    toastContainer.className = 'fixed bottom-4 right-4 flex flex-col gap-2'
    document.body.appendChild(toastContainer)
  }
  return toastContainer
}

const showToast = (message: string, variant: 'success' | 'error') => {
  const container = ensureContainer()
  const toast = document.createElement('div')
  toast.className = `rounded-md px-4 py-3 text-sm shadow ${
    variant === 'success' ? 'bg-emerald-500 text-white' : 'bg-rose-600 text-white'
  }`
  toast.textContent = message
  container.appendChild(toast)
  setTimeout(() => {
    toast.classList.add('opacity-0', 'transition-opacity', 'duration-500')
    toast.addEventListener('transitionend', () => toast.remove(), { once: true })
  }, 2000)
}

export const showSuccess = (message: string) => showToast(message, 'success')
export const showError = (message: string) => showToast(message, 'error')
