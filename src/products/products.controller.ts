import {
  Body,
  Controller,
  Delete,
  Get,
  Param,
  Post,
  Put,
  Query,
} from '@nestjs/common';
import { ProductService } from './products.service';
import { Product } from './schemas/product.schema';
import { createProductDto } from './dto/create-product.dto';
import { updateProductDto } from './dto/update-product.dto';

import { Query as ExpressQuery } from 'express-serve-static-core';

@Controller('products')
export class ProductsController {
  // eslint-disable-next-line prettier/prettier
  constructor(private productService: ProductService) { }

  @Get()
  async getAllProducts(@Query() query: ExpressQuery): Promise<{
    products: Product[];
    totalPages: number;
    totalProducts: number;
  }> {
    return this.productService.findAll(query);
  }

  @Get(':id')
  async getProductById(@Param('id') id: string): Promise<Product> {
    return this.productService.findById(id);
  }

  @Post('new')
  async createProduct(@Body() product: createProductDto): Promise<Product> {
    return this.productService.create(product);
  }

  @Put(':id')
  async updateProduct(
    @Param('id')
    id: string,
    @Body()
    product: updateProductDto,
  ): Promise<Product> {
    return this.productService.updateById(id, product);
  }

  @Delete(':id')
  async deleteProduct(
    @Param('id')
    id: string,
  ) {
    return this.productService.deleteProduct(id);
  }
}
