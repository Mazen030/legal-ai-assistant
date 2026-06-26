import axios from 'axios';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
});

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const queryDocument = async (sessionId, question) => {
  const response = await api.post('/query', {
    session_id: sessionId,
    question,
  });
  return response.data;
};

export const queryDocumentStream = (sessionId, question, onChunk, onDone, onError) => {
  fetch(`${API_BASE}/query/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, question }),
  })
    .then((response) => {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      const read = () => {
        reader.read().then(({ done, value }) => {
          if (done) { onDone(); return; }
          const text = decoder.decode(value);
          const lines = text.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const chunk = line.slice(6);
              if (chunk === '[DONE]') { onDone(); return; }
              if (chunk.startsWith('[ERROR]')) { onError(chunk); return; }
              onChunk(chunk);
            }
          }
          read();
        });
      };
      read();
    })
    .catch(onError);
};

export const deleteSession = async (sessionId) => {
  await api.delete(`/session/${sessionId}`);
};
