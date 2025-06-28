import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
import { useMutation } from "@tanstack/react-query";
import { queryClient, apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { BASE_URL } from "@/lib/constants";


export default function TransferModal({ isOpen, onClose, products = [], locations = [] }) {
  const { toast } = useToast();
  const [transferType, setTransferType] = useState("OUT");
  const [selectedProductId, setSelectedProductId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [locationId, setLocationId] = useState("");
  const [notes, setNotes] = useState("");

  const transferMutation = useMutation({
    mutationFn: (payload) => apiRequest("POST", `${BASE-URL}/stock_transfers`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`${BASE_URL}/products`] });
      toast({ title: "Success", description: "Stock transfer recorded" });
      onClose();
    },
    onError: (err) => {
      toast({
        title: "Error",
        description: err.message || "Could not record stock transfer",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!selectedProductId || !quantity || quantity <= 0) {
      toast({
        title: "Missing Fields",
        description: "Select a product and enter valid quantity",
        variant: "destructive",
      });
      return;
    }

    const payload = {
      transfer_type: transferType,
      location_id: locationId || null,
      notes,
      items: [
        {
          product_id: parseInt(selectedProductId),
          quantity: parseInt(quantity),
        },
      ],
    };

    transferMutation.mutate(payload);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Record Stock Transfer</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Select value={transferType} onValueChange={setTransferType}>
            <SelectTrigger>
              <SelectValue placeholder="Select transfer type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="OUT">OUT (Issue)</SelectItem>
              <SelectItem value="IN">IN (Receive)</SelectItem>
            </SelectContent>
          </Select>

          <Select value={selectedProductId} onValueChange={setSelectedProductId}>
            <SelectTrigger>
              <SelectValue placeholder="Select product" />
            </SelectTrigger>
            <SelectContent>
              {products.map((p) => (
                <SelectItem key={p.id} value={p.id.toString()}>
                  {p.name} ({p.sku})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Input
            type="number"
            placeholder="Quantity"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            min="1"
          />

          <Select value={locationId} onValueChange={setLocationId}>
            <SelectTrigger>
              <SelectValue placeholder="Optional: Destination Location" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">None</SelectItem>
              {locations.map((loc) => (
                <SelectItem key={loc.id} value={loc.id.toString()}>
                  {loc.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Textarea
            placeholder="Optional notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />

          <Button type="submit" className="w-full" disabled={transferMutation.isPending}>
            {transferMutation.isPending ? "Submitting..." : "Submit Transfer"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
