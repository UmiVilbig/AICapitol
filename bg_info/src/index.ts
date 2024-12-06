import mongoose from "mongoose";
import { Committee, Member, Membership } from "./functions";

class Main {
  constructor() {
    this.start();
  }

  private async start(): Promise<void> {
    await mongoose.connect('mongodb://localhost:27017/insider');
    console.log('Connected to MongoDB');
    // new Member();
    // new Committee();
    new Membership();
  }
}

new Main();