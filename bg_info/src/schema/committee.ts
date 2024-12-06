import * as mongoose from 'mongoose';

const committteeSchema = new mongoose.Schema({
  name: String, // full name of the congressmen
  type: String, // house or senate
  thomas_id: {type: String, unique: true }, // thomas id
  jurisdiction: String, // jurisdiction of the committee
  subcommittees: [{
    name: String, // name of the subcommittee
    thomas_id: String, // thomas
  }], // list of subcommittee thomas ids
  members: [{
    name: String, // full name of the congressmen
    rank: Number, // 1 for chair 2 for member
  }], // list of congressmen who are members of the committee
});

export type Committee = mongoose.InferSchemaType<typeof committteeSchema>;
export const Committee = mongoose.model('Committee', committteeSchema);