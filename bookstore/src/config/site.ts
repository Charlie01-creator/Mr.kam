/**
 * Initial content. Anything marked verified:false is shown to the owner as
 * "needs confirmation" and is editable from the admin dashboard.
 */
export const site = {
  name: "Kigundu Books", // TEMPORARY brand name: owner to confirm
  author: {
    // Spelling taken from the project brief; the physical cover is partly
    // illegible ("KAM…LEGEYA.K.MUBARAK"). Owner must confirm before launch.
    name: "Kawulugwa Mubarak Kigundu",
    verified: false,
  },
  currency: "UGX",
  country: "UG",
} as const;

export const knownBook = {
  slug: "essentials-of-applied-mathematics-in-statistics-and-numerical-methods",
  title: "Essentials of Applied Mathematics in Statistics and Numerical Methods",
  edition: "2025 Edition", // printed on the front cover
  verifiedFields: ["title", "edition"],
  // Deliberately absent: price, ISBN, stock, publication details.
} as const;
