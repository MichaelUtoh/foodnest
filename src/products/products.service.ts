import { Injectable, NotFoundException } from '@nestjs/common';
import { Product } from './schemas/product.schema';
import * as mongoose from 'mongoose';
import { InjectModel } from '@nestjs/mongoose';
import { Query } from 'express-serve-static-core';

@Injectable()
export class ProductService {
  constructor(
    @InjectModel(Product.name)
    private productModel: mongoose.Model<Product>,
    // eslint-disable-next-line prettier/prettier
  ) { }

  async findAll(query: Query): Promise<{
    products: Product[];
    totalPages: number;
    totalProducts: number;
  }> {
    const params: any = {};
    const resPerPage = 10;
    const currentPage = Number(query.page) || 1;
    const skip = resPerPage * (currentPage - 1);
    for (const key in query) {
      if (query[key] && key !== 'page') {
        console.log(key);
        params[key] = { $regex: query[key], $options: 'i' }; // Case-insensitive search
      }
    }

    const totalProducts = await this.productModel.countDocuments({ ...params });
    const totalPages = Math.ceil(totalProducts / resPerPage);
    const products = await this.productModel
      .find({ ...params })
      .limit(resPerPage)
      .skip(skip);
    return { products, totalPages, totalProducts };
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
