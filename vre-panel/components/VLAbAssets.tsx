import {JWT} from "next-auth/jwt";
import {Tab} from '@headlessui/react'
import clsx from "clsx"
import WorkflowRuns from "./VLabAssets/WorkflowRuns";
import DataProducts from "./VLabAssets/DataProducts";
import GeoDataProducts from "./VLabAssets/GeoDataProducts";
import {Fragment} from "react";


type Props = {
  slug: string | string[] | undefined,
  isAuthenticated: boolean,
  token: JWT,
}

const tabs = [
  {
    title: "Workflow runs",
    panelComponent: WorkflowRuns,
  },
  {
    title: "Data Products",
    panelComponent: DataProducts,
  },
  {
    title: "Geographic data products",
    panelComponent: GeoDataProducts,
  },
]

const VLabAssets: React.FC<Props> = ({slug, isAuthenticated, token}) => {

  return (
    <div className="space-y-8">
      <p className="text-2xl font-sans">Assets</p>
      <Tab.Group>
        <Tab.List className="mb-5 flex list-none flex-col pl-0 sm:flex-row">
          {tabs.map((tab) => {
            return (
              <Tab as={Fragment}>
                {({selected}) => (
                  /* Use the `selected` state to conditionally style the selected tab. */
                  <button
                    className={clsx(
                      "py-1 px-8 max-h-16",
                      selected ? "bg-gray-500 text-white" : "text-gray-500 hover:text-black",
                    )}
                  >
                    {tab.title}
                  </button>
                )}
              </Tab>
            )
          })}
        </Tab.List>
        <Tab.Panels>
          <Tab.Panel>
            <WorkflowRuns slug={slug} isAuthenticated={isAuthenticated} token={token}/>
          </Tab.Panel>
          <Tab.Panel>
            <DataProducts slug={slug} isAuthenticated={isAuthenticated} token={token}/>
          </Tab.Panel>
          <Tab.Panel>
            <GeoDataProducts slug={slug} isAuthenticated={isAuthenticated} token={token}/>
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  )
}

export default VLabAssets
