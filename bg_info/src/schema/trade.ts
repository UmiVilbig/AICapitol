import * as mongoose from 'mongoose';

const tradeSchema = new mongoose.Schema({
  id: { type: String, unique: true}, // unique identifier
  name: String, // full name of the congressmen
  trade_date: Date, // date of the trade
  reportedDate: Date, // date the trade was reported
  ticker: String, // stock ticker
  asset: String, // stock name
  tradeType: String, // buy or sell
  tradeValue: Number, // value of the trade
  owner: String, // congressmen who made the trade or their spouse
});

export type Trade = mongoose.InferSchemaType<typeof tradeSchema>;
export const Trade = mongoose.model('Trade', tradeSchema);