import fs from 'fs';
import path from 'path';
import type { IMember } from '../interface/member';
import { Congressmen } from '../schema';

class Member {
  private members: IMember[] = [];
  constructor() {
    this.start();
  };

  private start(): void {
    this.loadData();
    this.addToDB();
  }

  private loadData(): void {
    const data = fs.readFileSync(path.join(__dirname, `../../data/members.json`), 'utf8');
    this.members = JSON.parse(data) as IMember[];
  }

  private addToDB(): void {
    this.members.forEach(async (member) => {
      const name = member.name.official_full? member.name.official_full : member.name.first + ' ' + member.name.last;
      const congressmen = new Congressmen({
        fullName: name,
        first: member.name.first,
        last: member.name.last,
        bioguide: member.id.bioguide,
        party: member.terms[0].party,
        state: member.terms[0].state,
        committees: []
      })
      await congressmen.save();
      console.log(`Added ${name} to the database`);
    });
    console.log('All members added to the database');
  }
}

export { Member };