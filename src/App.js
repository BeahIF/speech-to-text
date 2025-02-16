
import React, { useState } from 'react';
import MicRecorder from 'mic-recorder-to-mp3';
import axios from 'axios';

const App = () => {
  const [text, setText] = useState('');
  const [recorder, setRecorder] = useState(null);

  const startRecording = () => {
    const mp3Recorder = new MicRecorder({ bitRate: 128 });
    mp3Recorder.start().then(() => setRecorder(mp3Recorder));
  };

  const stopRecording = async () => {
    console.log('Parando gravação...');

    const [buffer, blob] = await recorder.stop().getMp3();
    console.log('Áudio capturado:', blob);

    const formData = new FormData();
    formData.append('file', blob, 'audio.mp3');
    console.log('FormData criado:', formData);
    try {
      const response = await axios.post('http://localhost:5000/transcribe', formData);
      console.log('Resposta do backend:', response.data);
      setText(response.data.text);
    } catch (error) {
      console.error('Erro ao enviar para backend:', error);
    }
  };

  return (
    <div>
      <button onClick={startRecording}>Gravar</button>
      <button onClick={stopRecording}>Parar e Transcrever</button>
      <p>Texto Capturado: {text}</p>
    </div>
  );
};

export default App;