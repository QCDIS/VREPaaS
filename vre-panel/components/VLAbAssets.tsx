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
              <Tab as={Fragment} key={tab.title}>
                {({selected}) => (
                  /* Use the `selected` state to conditionally style the selected tab. */
                  <button
                    className={clsx(
                      "py-1 px-8 max-h-16",
                      selected ? "bg-secondary text-onSecondary" : "bg-surface text-primaryMuted hover:text-black",
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
          {tabs.map((tab) => {
            return (
              <Tab.Panel as={Fragment} key={tab.title}>
                <tab.panelComponent slug={slug} isAuthenticated={isAuthenticated} token={token}/>
              </Tab.Panel>
            )
          })}
        </Tab.Panels>
      </Tab.Group>
    </div>
  )
}

export default VLabAssets
