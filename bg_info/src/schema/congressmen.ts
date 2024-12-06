import * as mongoose from 'mongoose';

const congressmenScehma = new mongoose.Schema({
  fullName: { type: String }, // full name of the congressmen
  first: { type: String }, // first name of the congressmen
  last: { type: String }, // last name of the congressmen
  bioguide: { type: String, unique: true }, // bioguide id
  party: String, // political party
  state: String, // state the congressmen represents
  committees: [{ type: String, ref: 'Committee' }], // list of committees the congressmen is a member
  txs: [{ type: mongoose.Schema.Types.ObjectId, ref: 'trades' }], // list of trades the congressmen is involved in
});

export type Congressmen = mongoose.InferSchemaType<typeof congressmenScehma>;
export const Congressmen = mongoose.model('Congressmen', congressmenScehma);