import React from "react";
import Link from "next/link";

const Footer: React.FC = () => {

  return (
    <div className="flex flex-col w-full items-center mb-2">
      <p className="text-xs text-gray-700">
        Powered by NaaVRE / LifeWatch ERIC VLIC (
          <Link
            href="/about"
            className="hover:underline"
          >
            About
          </Link>
        )
      </p>
    </div>
  )
}

export default Footer
