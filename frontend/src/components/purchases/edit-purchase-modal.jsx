import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQuery } from "@tanstack/react-query";

import { apiRequest, queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { BASE_URL } from "@/lib/constants";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";

import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

import { Trash2, Trash } from "lucide-react";

// Schema
const formSchema = z.object({
  supplier_id: z.coerce.number().min(1, "Supplier is required"),
  total_cost: z.string().min(1, "Total cost is required"),
  notes: z.string().optional(),
});

export default function EditPurchaseModal({ isOpen, onClose, purchase }) {
  const { toast } = useToast();
  const [items, setItems] = useState([]);

  const isEditable = useMemo(() => {
    if (!purchase?.purchase_date) return false;
    const purchaseDate = new Date(purchase.purchase_date);
    const now = new Date();
    const diffInDays = (now - purchaseDate) / (1000 * 60 * 60 * 24);
    return diffInDays <= 30;
  }, [purchase]);

  const { data: suppliers = [] } = useQuery({
    queryKey: [`${BASE_URL}/suppliers`],
    queryFn: async () => {
      const res = await fetch(`${BASE_URL}/suppliers`);
      if (!res.ok) throw new Error("Failed to fetch suppliers");
      return res.json();
    },
  });

  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      supplier_id: purchase?.supplier_id ?? undefined,
      total_cost: purchase?.total_cost?.toString() ?? "0",
      notes: purchase?.notes ?? "",
    },
  });

  useEffect(() => {
    if (purchase) {
      form.reset({
        supplier_id: purchase.supplier_id,
        total_cost: purchase.total_cost?.toString() ?? "0",
        notes: purchase.notes ?? "",
      });
      setItems(purchase.items ?? []);
    }
  }, [purchase, form]);

  const handleItemChange = (itemId, field, value) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === itemId ? { ...item, [field]: value } : item
      )
    );
  };

  const handleItemDelete = async (itemId) => {
    try {
      await apiRequest("DELETE", `${BASE_URL}/purchase_items/${itemId}`);
      setItems((prev) => prev.filter((item) => item.id !== itemId));
      toast({
        title: "Item removed",
        description: `Item ${itemId} removed successfully`,
      });
    } catch (error) {
      toast({
        title: "Failed to delete item",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const updateMutation = useMutation({
    mutationFn: async (data) => {
      await apiRequest("PUT", `${BASE_URL}/purchases/${purchase.id}`, data);

      await Promise.all(
        items.map((item) =>
          apiRequest("PUT", `${BASE_URL}/purchase_items/${item.id}`, {
            quantity: parseInt(item.quantity),
            unit_cost: parseFloat(item.unit_cost),
          })
        )
      );
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: [`${BASE_URL}/purchases`] });

      toast({
        title: "Purchase updated",
        description: `Purchase #${purchase.id} updated successfully`,
      });

      onClose();
      window.location.href = "/purchases";
    },
    onError: (error) => {
      toast({
        title: "Update failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => apiRequest("DELETE", `${BASE_URL}/purchases/${purchase.id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`${BASE_URL}/purchases`] });
      toast({
        title: "Deleted",
        description: `Purchase #${purchase.id} deleted`,
      });
      onClose();
    },
    onError: (error) => {
      toast({
        title: "Delete failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const onSubmit = (data) => {
    const newTotal = items.reduce((acc, item) => {
      const q = parseInt(item.quantity) || 0;
      const c = parseFloat(item.unit_cost) || 0;
      return acc + q * c;
    }, 0);
    data.total_cost = newTotal.toFixed(2);
    updateMutation.mutate(data);
  };

  if (!purchase) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold text-gray-800">
            Edit Purchase #{purchase.id}
          </DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            {/* Supplier */}
            <FormField
              control={form.control}
              name="supplier_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Supplier</FormLabel>
                  <Select
                    value={field.value?.toString() ?? ""}
                    onValueChange={(value) => field.onChange(parseInt(value))}
                    disabled={!isEditable}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select supplier" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {suppliers.map((supplier) => (
                        <SelectItem key={supplier.id} value={supplier.id.toString()}>
                          {supplier.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Notes */}
            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notes</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Update notes..."
                      {...field}
                      disabled={!isEditable}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Purchase Items */}
            <div className="space-y-3">
              <h4 className="text-md font-semibold text-gray-700">Purchase Items</h4>
              {items.map((item) => {
                const quantity = parseInt(item.quantity) || 0;
                const unitCost = parseFloat(item.unit_cost) || 0;
                const subtotal = (quantity * unitCost).toFixed(2);

                return (
                  <div key={item.id} className="flex items-center gap-2 flex-wrap">
                    <div className="flex-1 min-w-[120px]">
                      <p className="text-sm text-gray-700 font-medium">{item.product?.name}</p>
                    </div>
                    <Input
                      type="number"
                      className="w-20"
                      min="1"
                      value={item.quantity}
                      onChange={(e) => handleItemChange(item.id, "quantity", e.target.value)}
                      disabled={!isEditable}
                    />
                    <Input
                      type="number"
                      className="w-24"
                      min="0"
                      step="0.01"
                      value={item.unit_cost}
                      onChange={(e) => handleItemChange(item.id, "unit_cost", e.target.value)}
                      disabled={!isEditable}
                    />
                    <span className="text-sm text-gray-600 w-20">
                      KSH{subtotal}
                    </span>
                    {isEditable && (
                      <Button
                        type="button"
                        variant="ghost"
                        onClick={() => handleItemDelete(item.id)}
                      >
                        <Trash className="w-4 h-4 text-red-500" />
                      </Button>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Total Cost */}
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700">Total Cost</label>
              <Input
                type="text"
                readOnly
                value={`KSH ${items
                  .reduce((sum, item) => sum + item.quantity * item.unit_cost, 0)
                  .toFixed(2)}`}
                className="bg-gray-100"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3 pt-4">
              {isEditable ? (
                <>
                  <Button
                    type="button"
                    variant="destructive"
                    className="flex-1"
                    onClick={() => deleteMutation.mutate()}
                    disabled={deleteMutation.isPending}
                  >
                    {deleteMutation.isPending ? "Deleting..." : "Delete"}
                    <Trash2 className="ml-2 h-4 w-4" />
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1 bg-blue-600 hover:bg-blue-700"
                    disabled={updateMutation.isPending}
                  >
                    {updateMutation.isPending ? "Updating..." : "Update Purchase"}
                  </Button>
                </>
              ) : (
                <Button type="button" className="w-full" onClick={onClose}>
                  Close
                </Button>
              )}
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}