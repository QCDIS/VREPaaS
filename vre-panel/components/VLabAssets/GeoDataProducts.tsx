import dynamic from "next/dynamic";
const CatalogMapView = dynamic(() => import("./catalog_map"), {ssr: false})

type Props = {
  slug: string | string[] | undefined,
}

const GeoDataProducts: React.FC<Props> = ({slug}) => {

  return (
    <div>
      <div className="h-72 mt-5">
        <CatalogMapView vlab_slug={slug}/>
      </div>
    </div>
  )
}

export default GeoDataProducts
