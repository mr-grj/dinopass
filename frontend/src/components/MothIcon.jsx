const MothIcon = ({ withAntennae = true, ...props }) => (
  <svg viewBox="0 0 100 100" fill="currentColor" role="img" aria-label="CipherMoth" {...props}>
    <path d="M50 24 C46 24 44 29 44 37 C44 53 47 69 50 82 C53 69 56 53 56 37 C56 29 54 24 50 24 Z" />
    <circle cx="50" cy="21" r="5" />
    <path d="M50 30 C66 21 80 19 88 23 C91 31 88 44 81 49 C69 53 58 51 50 50 Z" />
    <path d="M50 53 C63 53 75 59 78 68 C80 77 73 83 65 82 C57 80 52 72 50 70 Z" />
    <path d="M50 30 C34 21 20 19 12 23 C9 31 12 44 19 49 C31 53 42 51 50 50 Z" />
    <path d="M50 53 C37 53 25 59 22 68 C20 77 27 83 35 82 C43 80 48 72 50 70 Z" />
    {withAntennae && (
      <>
        <g fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
          <path d="M52 18 C58 11 65 9 70 10" />
          <path d="M48 18 C42 11 35 9 30 10" />
        </g>
        <circle cx="70" cy="10" r="2.4" />
        <circle cx="30" cy="10" r="2.4" />
      </>
    )}
  </svg>
);

export default MothIcon;
