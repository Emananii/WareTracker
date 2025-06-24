import { z } from "zod";

// Business form validation
export const insertBusinessSchema = z.object({
  name: z.string().min(2, "Business name must be at least 2 characters."),
  address: z.string().min(5, "Address must be at least 5 characters."),
});

// Category form validation
export const insertCategorySchema = z.object({
  name: z.string().min(2, "Category name must be at least 2 characters."),
});

// Supplier form validation
export const insertSupplierSchema = z.object({
  name: z.string().min(2),
  contact: z.string().optional(),
  email: z.string().email("Invalid email").optional(),
  phone: z.string().min(5).optional(),
});

// Unit form validation
export const insertUnitSchema = z.object({
  name: z.string().min(2),
  abbreviation: z.string().min(1),
  baseUnit: z.string().optional(),
  conversionFactor: z.coerce.number().nonnegative().default(1),
  isBaseUnit: z.boolean().default(false),
});

// Inventory Item form validation
export const insertInventoryItemSchema = z.object({
  name: z.string().min(2),
  sku: z.string().min(1),
  quantity: z.coerce.number().nonnegative().default(0),
  minStock: z.coerce.number().nonnegative().default(0),
  location: z.string().optional(),
  categoryId: z.coerce.number().optional(),  // can be required if strict
  unitId: z.coerce.number().optional(),      // can be required if strict
  unitCost: z.coerce.number().nonnegative().optional(),
});

// Purchase form validation
export const insertPurchaseSchema = z.object({
  supplierId: z.coerce.number().optional(), // can be required if needed
  totalCost: z.coerce.number().nonnegative(),
  notes: z.string().optional(),
});

// Purchase Item form validation
export const insertPurchaseItemSchema = z.object({
  purchaseId: z.coerce.number(),
  inventoryItemId: z.coerce.number(),
  quantity: z.coerce.number().nonnegative(),
  unitCost: z.coerce.number().nonnegative(),
});

// Movement form validation
export const insertMovementSchema = z.object({
  inventoryItemId: z.coerce.number(),
  businessId: z.coerce.number().optional(),
  type: z.enum(["out_to_business", "in_from_business", "adjustment"]),
  quantity: z.coerce.number().nonnegative(),
  notes: z.string().optional(),
});
