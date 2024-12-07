import fs from 'fs';
import path from 'path';
import type { ICommitteeMembership } from '../interface/committee';
import { Congressmen, Committee, Subcommittee } from '../schema';

class Membership {
  private data: ICommitteeMembership = {} as ICommitteeMembership;
  constructor() {};

  public async start(): Promise<void> {
    await this.loadData();
    await this.addToDB();
  }

  private async loadData(): Promise<void> {
    const data = fs.readFileSync(path.join(__dirname, `../../data/committee_mem.json`), 'utf8');
    this.data = JSON.parse(data) as ICommitteeMembership;
  }

  private async addToDB(): Promise<void> {
    Object.keys(this.data).forEach(async (committee) => {
      const isSub = committee.search(/\d/) !== -1;
      if(isSub) {
        const subcom = await Subcommittee.findOne({ thomas_id: committee })
        if(subcom) {
          this.data[committee].forEach(async(member) => {
            subcom.members.push({
              name: member.name,
              rank: member.rank,
            })
            if (subcom.name) {
              this.updateCongressmen(subcom.name, member.bioguide);
            }
          })
          await subcom.save();
        }
      } else {
        const com = await Committee.findOne({ thomas_id: committee });
        if(com) {
          this.data[committee].forEach(async(member) => {
            com.members.push({
              name: member.name,
              rank: member.rank,
            })
            if (com.name) {
              this.updateCongressmen(com.name, member.bioguide);
            }
          })
          await com.save();
        }
      }
    })
  }

  private async updateCongressmen(committeeName: string, bioguide: string): Promise<void> {
    const congressman = await Congressmen.findOne({ bioguide });
    if(congressman) {
      congressman.committees.push(committeeName);
      await congressman.save();
    }
  }
}

export { Membership };