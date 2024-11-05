import { Injectable, NotFoundException } from '@nestjs/common';
import { Product } from './schemas/product.schema';
import * as mongoose from 'mongoose';
import { InjectModel } from '@nestjs/mongoose';

@Injectable()
export class ProductService {
  constructor(
    @InjectModel(Product.name)
    private productModel: mongoose.Model<Product>,
    // eslint-disable-next-line prettier/prettier
  ) { }

  async findAll(): Promise<Product[]> {
    const products = await this.productModel.find();
    return products;
  }

  async findById(id: string): Promise<Product> {
    const res = await this.productModel.findById(id);

    if (!res) {
      throw new NotFoundException('Product not found');
    }
    return res;
  }

  async create(product: Product): Promise<Product> {
    const res = await this.productModel.create(product);
    return res;
  }

  async updateById(id: string, product: Product): Promise<Product> {
    return await this.productModel.findByIdAndUpdate(id, product, {
      new: true,
      runValidators: true,
    });
  }

  async deleteProduct(id: string) {
    return await this.productModel.findByIdAndDelete(id);
  }
}
