import * as mongoose from 'mongoose';

const subcommittteeSchema = new mongoose.Schema({
  name: { type: String, unique: true }, // full name of the congressmen
  thomas_id: String, // thomas id
  members: [{
    name: String, // full name of the congressmen
    rank: Number, // 1 for chair 2 for member
  }], // list of congressmen who are members of the committee
});

export type Subcommittee = mongoose.InferSchemaType<typeof subcommittteeSchema>;
export const Subcommittee = mongoose.model('Subcommittee', subcommittteeSchema);