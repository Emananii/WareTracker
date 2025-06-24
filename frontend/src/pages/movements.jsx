import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Plus, ArrowRight, ArrowLeft, RotateCcw } from "lucide-react";
import AddMovementModal from "@/components/movements/add-movement-modal";

export default function Movements() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const { data: movements = [], isLoading } = useQuery({
    queryKey: ["/api/movements"],
  });

  const { data: items = [] } = useQuery({
    queryKey: ["/api/inventory"],
  });

  const { data: businesses = [] } = useQuery({
    queryKey: ["/api/businesses"],
  });

  const formatDate = (date) => {
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(date));
  };

  const getItemName = (itemId) => {
    const item = items.find((i) => i.id === itemId);
    return item ? `${item.name} (${item.sku})` : "Unknown Item";
  };

  const getBusinessName = (businessId) => {
    if (!businessId) return "N/A";
    const business = businesses.find((b) => b.id === businessId);
    return business?.name || "Unknown Business";
  };

  const getMovementIcon = (type) => {
    switch (type) {
      case "out_to_business":
        return <ArrowRight className="h-4 w-4" />;
      case "in_from_business":
        return <ArrowLeft className="h-4 w-4" />;
      case "adjustment":
        return <RotateCcw className="h-4 w-4" />;
      default:
        return null;
    }
  };

  const getMovementBadge = (type) => {
    switch (type) {
      case "out_to_business":
        return (
          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
            Out to Business
          </Badge>
        );
      case "in_from_business":
        return (
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
            In from Business
          </Badge>
        );
      case "adjustment":
        return (
          <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">
            Adjustment
          </Badge>
        );
      default:
        return <Badge variant="outline">{type}</Badge>;
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Card className="animate-pulse">
          <CardContent className="p-6">
            <div className="h-20 bg-gray-200 rounded"></div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-800">Inventory Movements</h1>
        <Button onClick={() => setIsAddModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Movement
        </Button>
      </div>

      {/* Movements Table */}
      <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="bg-gray-50">
                <TableHead>Type</TableHead>
                <TableHead>Item</TableHead>
                <TableHead>Business</TableHead>
                <TableHead>Quantity</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Notes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {movements.length > 0 ? (
                movements
                  .sort((a, b) => new Date(b.movementDate).getTime() - new Date(a.movementDate).getTime())
                  .map((movement) => (
                    <TableRow key={movement.id} className="hover:bg-gray-50">
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          {getMovementIcon(movement.type)}
                          {getMovementBadge(movement.type)}
                        </div>
                      </TableCell>
                      <TableCell>{getItemName(movement.inventoryItemId)}</TableCell>
                      <TableCell>{getBusinessName(movement.businessId)}</TableCell>
                      <TableCell className="font-medium">{movement.quantity}</TableCell>
                      <TableCell>{formatDate(movement.movementDate)}</TableCell>
                      <TableCell>{movement.notes || "N/A"}</TableCell>
                    </TableRow>
                  ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                    No movements found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </Card>

      <AddMovementModal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} />
    </div>
  );
}
