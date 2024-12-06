export interface IMember {
  id: {
    bioguide: string;
  }
  name: {
    first: string;
    last: string;
    official_full: string;
  },
  terms: [
    {
      type: string;
      start: string;
      end: string;
      state: string;
      party: string;
    }
  ]
}