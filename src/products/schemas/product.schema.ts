import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';

export enum ProductCategory {
  FRUIT = 'Fruit',
  TUBER = 'Tuber',
  GRAIN = 'Grain',
}

@Schema({
  timestamps: true,
})
export class Product {
  @Prop()
  name: string;

  @Prop()
  description: string;

  @Prop()
  price: string;

  @Prop()
  category: ProductCategory;
}

export const ProductSchema = SchemaFactory.createForClass(Product);
