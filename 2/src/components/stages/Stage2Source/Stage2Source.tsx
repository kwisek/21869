import { Howl } from "howler";
import { useRef, useState } from "react";
import InputOption from "../../../enums/InputOption";
import Stage from "../../../enums/Stage";
import layoutStyles from '../../../styles/modules/layout.module.scss';
import controlsStyles from '../../../styles/modules/controls.module.scss';
import stageStyles from './Stage2Source.module.scss';

type StageSourceProps = {
  setStage: (stage: Stage) => void;
  setInputDataBlob: (inputDataBlob: Blob) => void;
};

function StageSource(props: StageSourceProps) {

  const [howl, setHowl] = useState<Howl | null>(null);
  const [inputFile, setInputFile] = useState<File | null>(null);
  const [inputBlob, setInputBlob] = useState<Blob | null>(null);
  const [isRecording, setIsRecording] = useState<boolean>(false);

  const [selectedInput, setSelectedInput] = useState<InputOption | null>(null);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);

  const chunksRef = useRef<Blob[]>([]);
  const inputFileRef = useRef<HTMLInputElement>(null);

  const nextStage = (blob: Blob) => {
    props.setInputDataBlob(blob);
    props.setStage(Stage.CONVERT);
  };

  const playFromFile = () => {
    if (!inputFile) return;
    const localHowl = new Howl({
      src: [URL.createObjectURL(inputFile)],
      format: [inputFile.type.split("/")[1]],
    });
    localHowl?.once("end", stopPlaying);
    localHowl.play();
    setHowl(localHowl);
  };

  const playRecording = () => {
    if (!inputBlob) return;
    const localHowl = new Howl({
      src: [URL.createObjectURL(inputBlob)],
      format: ["webm"],
    });
    localHowl?.once("end", stopPlaying);
    localHowl.play();
    setHowl(localHowl);
  };

  const stopPlaying = () => {
    howl?.stop();
    setHowl(null);
  };

  const clearInputFile = () => {
    stopPlaying();
    setInputFile(null);
  };

  const clearInputBlob = () => {
    stopPlaying();
    setInputBlob(null);
  };

  const handleDrop = (e: any) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setInputFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: any) => {
    if (e.target.files && e.target.files.length > 0) {
      setInputFile(e.target.files[0]);
    }
  };

  const handleDropAreaClick = (e: any) => {
    inputFileRef.current?.click();
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      setMediaRecorder(recorder);

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        setInputBlob(blob);
      };

      chunksRef.current = [];
      recorder.start();
      setIsRecording(true);

    } catch (err) {
      console.error("Microphone access denied:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }

    setIsRecording(false);
  };

  return (
    <div className={layoutStyles.contentContainerCentered}>
      <h2>Wybierz źródło</h2>
      <p>System wspiera wgranie pliku muzycznego z dysku, lub użycie mikrofonu wbudowanego w to urządzenie.</p>
      <div className={stageStyles.inputOptionsContainer}>
        <div className={stageStyles.inputOption} style={selectedInput === InputOption.MICROPHONE ? { opacity: 1.0 } : { opacity: 0.5 }}>
          {selectedInput !== InputOption.MICROPHONE && (
            <div className={stageStyles.inputOptionOverlay} onClick={() => setSelectedInput(InputOption.MICROPHONE)}>
              <p>Mikrofon</p>
              <i>(Kliknij aby wybrać)</i>
            </div>
          )}

          {selectedInput === InputOption.MICROPHONE && (
            <div className={stageStyles.inputOptionContent}>
              {inputBlob === null && isRecording === false && (
                <div className={stageStyles.inputControlsContainer}>
                  <div className={stageStyles.inputControlsRow}>
                    <i><center>Wciśnij przycisk, aby rozpocząć nagrywanie.</center></i> 
                  </div>
                  <div className={stageStyles.inputControlsRow}>
                    <div className={[controlsStyles.btnPrimary, controlsStyles.blue].join(" ")} onClick={startRecording}>&#11044; 
                      Nagraj
                    </div>
                  </div>
                </div>
              )}
    
              {inputBlob === null && isRecording !== false && (
                <div className={stageStyles.inputControlsContainer}>
                  <div className={layoutStyles.inputControlsRow}>
                    <i>Nagrywanie...</i>
                  </div>
                  <div className={layoutStyles.inputControlsRow}>
                    <div className={[controlsStyles.btnPrimary, controlsStyles.red].join(" ")} onClick={stopRecording}>
                      &#9632; Stop
                    </div>
                  </div>
                </div>
              )}

              {inputBlob !== null && isRecording === false && (
                <>
                
                <div className={stageStyles.inputControlsRow}>
                  <center>
                    Nagranie gotowe <br />
                    <div className={stageStyles.inputSize}>(Rozmiar: {inputBlob.size} bajtów)</div>
                  </center>
                </div>

                  <div className={stageStyles.inputControlsRow}>
                    {howl === null && (
                      <div className={[controlsStyles.btnPrimary, controlsStyles.blue].join(" ")} onClick={playRecording}>
                        &#9654; Odtwórz
                      </div>
                    )}
                    {howl !== null && (
                      <div className={[controlsStyles.btnPrimary, controlsStyles.blue].join(" ")} onClick={stopPlaying}>
                        &#9632; Stop
                      </div>
                    )}
                  </div>

                  <div className={stageStyles.inputControlsRow}>
                    <div className={[controlsStyles.btnPrimary, controlsStyles.red].join(' ')} onClick={clearInputBlob}>
                      &#10007; Odrzuć
                    </div>
                    <div className={[controlsStyles.btnPrimary, controlsStyles.green].join(' ')} onClick={() => nextStage(inputBlob)}>
                      &#10003; Zaakceptuj
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        <div className={stageStyles.inputOption} style={selectedInput === InputOption.UPLOAD_FILE ? { opacity: 1.0 } : { opacity: 0.5 }}>
          {selectedInput !== InputOption.UPLOAD_FILE && (
            <div
              className={stageStyles.inputOptionOverlay}
              onClick={() => setSelectedInput(InputOption.UPLOAD_FILE)}
            >
              <p>Wgraj plik z dysku</p>
              <i>(Kliknij aby wybrać)</i>
            </div>
          )}

          {!inputFile && selectedInput === InputOption.UPLOAD_FILE && (
            <div className={stageStyles.inputUploadContainer} onClick={handleDropAreaClick} onDrop={handleDrop}>
              <input type="file" ref={inputFileRef} onChange={handleFileChange} style={{ display: "none" }}/>
              <i><center>Upuść plik tutaj</center></i>
              <i><center>Lub kliknij, aby wybrać go z dysku</center></i>
            </div>
          )}

          {inputFile && (
            <center>
              <div className={stageStyles.inputControlsRow}>
                <center>
                  Załadowany plik: <b>{inputFile.name}</b> <br />
                  <div className={stageStyles.inputSize}>(Rozmiar: {inputFile.size} bajtów)</div>
                </center>
              </div>

              <div className={stageStyles.inputControlsRow}>
                {howl === null && <div className={[controlsStyles.btnPrimary, controlsStyles.blue].join(' ')} onClick={playFromFile}>
                  &#9654; Odtwórz
                </div>}
                {howl !== null && <div className={[controlsStyles.btnPrimary, controlsStyles.blue].join(' ')} onClick={stopPlaying}>
                  &#9632; Stop
                </div>}
              </div>

              <div className={stageStyles.inputControlsRow}>
                <div className={[controlsStyles.btnPrimary, controlsStyles.red].join(' ')} onClick={clearInputFile}>
                  &#10007; Odrzuć
                </div>
                <div className={[controlsStyles.btnPrimary, controlsStyles.green].join(' ')} onClick={() => nextStage(inputFile)}>
                  &#10003; Zaakceptuj
                </div>
              </div>
            </center>
          )}
        </div>
      </div>
    </div>
  );
}

export default StageSource;