import {VLab} from "../types/vlab";

type Props = {
  vlab: VLab,
  backendError: boolean,
}

const VLabDescription: React.FC<Props> = ({vlab, backendError}) => {

  return (
    <div>
      {backendError ? (
        <p className="my-5">
          Could not load vlab description
        </p>
      ) : (
        <>
          <p className="text-4xl font-sans">{vlab.title}</p>
          <p className="mt-5 text-justify">{vlab.description}</p>
        </>
      )}
    </div>
  )
}

export default VLabDescription
