import mongoose from "mongoose";
import { Committee, Member, Membership } from "./functions";

class Main {
  constructor() {
    this.start();
  }

  private async start(): Promise<void> {
    await mongoose.connect('mongodb://mongo:27017/insider');
    console.log('Connected to MongoDB');
    await this.sleep(2000);
    const initMember = new Member();
    const initCommittee = new Committee();
    const initMembership = new Membership();

    await initMember.start();
    await initCommittee.start();
    await initMembership.start();

    return process.exit(0);
  }

  private async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  };
}

new Main();