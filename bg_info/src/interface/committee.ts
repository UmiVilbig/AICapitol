export interface ICommittee {
  name: string;
  type: string; // house or senate
  thomas_id: string; // thomas id
  jurisdiction: string; // jurisdiction of the committee
  subcommittees: [{
    name: string; // name of the subcommittee
    thomas_id: string; // thomas id
  }];
}

export interface ICommitteeMembership {
  [key: string]: [
    {
      name: string;
      rank: number;
      bioguide: string;
    }
  ]
}