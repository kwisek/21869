import Notation from "../../../enums/Notation";
import Stage from "../../../enums/Stage";
import controlsStyles from '../../../styles/modules/controls.module.scss';
import layoutStyles from '../../../styles/modules/layout.module.scss';

type StageStartProps = {
  setStage: (stage: Stage) => void;
  notation: Notation;
  setNotation: (notation: Notation) => void;
};

function StageStart(props: StageStartProps) {

  return (
    <div className={layoutStyles.contentContainerCentered}>

      <center>
        <h2>Konwerter plików dźwiękowych na nuty do kalimby</h2>
        <p>Aplikacja umożliwia automatyczne przekonwertowanie wybranego utworu dźwiękowego na zapis nutowy do kalimby.</p>
        <p>Prototyp wspiera jedynie kalimbę 17-klawiszową w stojeniu C-dur.</p>
      </center>
      
      <div className={controlsStyles.controlsRow}>
        <br/><hr/><br/>
        <center style={{marginBottom: "5px"}}>Notacja używana w trakcie procesu:</center>
        <div className={controlsStyles.inlineControlsContainer}>
          <div className={`${controlsStyles.inlineControl} ${props.notation === Notation.STANDARD ? controlsStyles.active : ''}`} onClick={() => props.setNotation(Notation.STANDARD)}>(C4) Standardowa</div>
          <div className={`${controlsStyles.inlineControl} ${props.notation === Notation.NUMERIC ? controlsStyles.active : ''}`} onClick={() => props.setNotation(Notation.NUMERIC)}>(1&#176;) Numeryczna</div>
          <div className={`${controlsStyles.inlineControl} ${props.notation === Notation.LETTERED ? controlsStyles.active : ''}`} onClick={() => props.setNotation(Notation.LETTERED)}>(C&#176;) Literowa</div>
        </div>
        <br/><hr/><br/>
      </div>
      

      <div>
        <button className={`${controlsStyles.btnPrimary} ${controlsStyles.green}`} onClick={() => props.setStage(Stage.SOURCE)}>Rozpocznij</button>
      </div>
    </div>
  );
}

export default StageStart;