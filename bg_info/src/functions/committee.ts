import fs from 'fs';
import path from 'path';
import type { ICommittee } from '../interface/committee';
import { Committee as CommitteeDB, Subcommittee } from '../schema';

class Committee {
  private committee: ICommittee[] = [];
  constructor() {};

  public async start(): Promise<void> {
    await this.loadData();
    await this.addToDB();
  }

  private async loadData(): Promise<void> {
    const data = fs.readFileSync(path.join(__dirname, `../../data/committees.json`), 'utf8');
    this.committee = JSON.parse(data) as ICommittee[];
  }

  private async addToDB(): Promise<void> {
    this.committee.forEach(async (committee) => {
      const { subcommittees } = committee;
      console.log(subcommittees);
      const committeeRef = new CommitteeDB({
        name: committee.name,
        type: committee.type,
        thomas_id: committee.thomas_id,
        jurisdiction: committee.jurisdiction,
        subcommittees: subcommittees? subcommittees : [],
        members: [],
      })
      await committeeRef.save();
      console.log(`Added ${committee.name} to the database`);
      if(subcommittees) {
        subcommittees.forEach(async(subcommittee) => {
          const subCommitteeRef = new Subcommittee({
            name: subcommittee.name,
            thomas_id: `${committee.thomas_id}${subcommittee.thomas_id}`,
            members: [],
          });
          await subCommitteeRef.save();
          console.log(`Added ${subcommittee.name} to the database`);
        });
      }
    });
  }
}

export { Committee };