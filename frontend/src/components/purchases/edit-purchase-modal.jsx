import { useEffect, useMemo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQuery } from "@tanstack/react-query";

import { apiRequest, queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

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
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { X, Trash2 } from "lucide-react";

// Schema for editing (same as insert, but supplierId optional)
const formSchema = z.object({
  supplierId: z.number().min(1, "Supplier is required"),
  totalCost: z.string(),
  notes: z.string().optional(),
});

export default function EditPurchaseModal({ isOpen, onClose, purchase }) {
  const { toast } = useToast();

  const isEditable = useMemo(() => {
    if (!purchase?.purchaseDate) return false;
    const purchaseDate = new Date(purchase.purchaseDate);
    const now = new Date();
    const diffInDays = (now - purchaseDate) / (1000 * 60 * 60 * 24);
    return diffInDays <= 30;
  }, [purchase]);

  const { data: suppliers = [] } = useQuery({
    queryKey: ["/api/suppliers"],
  });

  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      supplierId: purchase?.supplierId || undefined,
      totalCost: purchase?.totalCost?.toString() || "0",
      notes: purchase?.notes || "",
    },
  });

  useEffect(() => {
    if (purchase) {
      form.reset({
        supplierId: purchase.supplierId,
        totalCost: purchase.totalCost?.toString(),
        notes: purchase.notes || "",
      });
    }
  }, [purchase, form]);

  const updateMutation = useMutation({
    mutationFn: async (data) => {
      return apiRequest("PUT", `/api/purchases/${purchase.id}`, data);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["/api/purchases"] });
      toast({
        title: "Purchase updated",
        description: `Purchase #${purchase.id} updated successfully`,
      });
      onClose();
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
    mutationFn: () => apiRequest("DELETE", `/api/purchases/${purchase.id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/purchases"] });
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
    updateMutation.mutate(data);
  };

  if (!purchase) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="text-lg font-semibold text-gray-800">
              Edit Purchase #{purchase.id}
            </DialogTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            {/* Supplier */}
            <FormField
              control={form.control}
              name="supplierId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Supplier</FormLabel>
                  <Select
                    onValueChange={(value) => field.onChange(parseInt(value))}
                    value={field.value?.toString()}
                    disabled={!isEditable}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select supplier" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {suppliers.map((supplier) => (
                        <SelectItem
                          key={supplier.id}
                          value={supplier.id.toString()}
                        >
                          {supplier.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Total Cost */}
            <FormField
              control={form.control}
              name="totalCost"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Total Cost</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      step="0.01"
                      {...field}
                      readOnly={!isEditable}
                      className={isEditable ? "" : "bg-gray-100"}
                    />
                  </FormControl>
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

            {/* Actions */}
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
