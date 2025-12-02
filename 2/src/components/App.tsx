import { useState } from 'react';
import Notation from '../enums/Notation';
import Stage from '../enums/Stage';
import layoutStyles from '../styles/modules/layout.module.scss';
import type { Sequence } from '../types/sequence';
import StageStart from './stages/Stage1Start/Stage1Start';
import StageSource from './stages/Stage2Source/Stage2Source';
import StageConvert from './stages/Stage3Convert/Stage3Convert';
import StageEdit from './stages/Stage4Edit/Stage4Edit';
import StageExport from './stages/Stage5Export/Stage5Export';
import StateBar from './util/StateBar/StateBar';

function App() {

  const [stage, setStage]= useState<Stage>(Stage.START);
  const [inputDataBlob, setInputDataBlob] = useState<Blob | null>(new Blob());
  const [notation, setNotation] = useState<Notation>(Notation.STANDARD);
  const [sequence, setSequence] = useState<Sequence | null>(null);

  return (
    <div className={layoutStyles.outerWrapper}>
      <div className={layoutStyles.innerWrapper}>
        <StateBar stage={stage} />
        <div className={layoutStyles.contentWrapper}>
          {stage === Stage.START && <StageStart setStage={setStage} notation={notation} setNotation={setNotation} />}
          {stage === Stage.SOURCE && <StageSource setStage={setStage} setInputDataBlob={setInputDataBlob} />}
          {stage === Stage.CONVERT && <StageConvert setStage={setStage} inputDataBlob={inputDataBlob!} setSequence={setSequence} notation={notation} />}
          {stage === Stage.EDIT && <StageEdit setStage={setStage} sequence={sequence!} setSequence={setSequence} notation={notation} />}
          {stage === Stage.EXPORT && <StageExport setStage={setStage} sequence={sequence!} notation={notation} />}
        </div>
      </div>
    </div>
  )
}

export default App;
