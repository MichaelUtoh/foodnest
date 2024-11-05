import { ProductCategory } from '../schemas/product.schema';

export class createProductDto {
  readonly name: string;
  readonly description: string;
  readonly price: string;
  readonly category: ProductCategory;
}
