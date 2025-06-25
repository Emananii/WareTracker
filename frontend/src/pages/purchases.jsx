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
import { Plus } from "lucide-react";

import AddPurchaseModal from "@/components/purchases/add-purchase-modal";
import EditPurchaseModal from "@/components/purchases/edit-purchase-modal";

// ---- MOCK DATA MODE ----
const MOCK_MODE = true;

const mockSuppliers = [
  { id: 1, name: "Acme Supplies Ltd" },
  { id: 2, name: "Global Traders Co." },
  { id: 3, name: "FreshFoods Warehouse" },
];

const mockPurchases = [
  {
    id: 101,
    supplierId: 1,
    totalCost: 1200.5,
    purchaseDate: "2025-06-01T14:30:00Z",
    notes: "Monthly restock",
  },
  {
    id: 102,
    supplierId: 2,
    totalCost: 785.75,
    purchaseDate: "2025-06-10T10:15:00Z",
    notes: "",
  },
  {
    id: 103,
    supplierId: 3,
    totalCost: 340.0,
    purchaseDate: "2025-06-15T08:45:00Z",
    notes: "Fruits and perishables",
  },
];

export default function Purchases() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingPurchase, setEditingPurchase] = useState(null);

  // --- DATA FETCHING ---
  const { data: purchases = [], isLoading } = useQuery({
    queryKey: ["/api/purchases"],
    enabled: !MOCK_MODE,
  });

  const { data: suppliers = [] } = useQuery({
    queryKey: ["/api/suppliers"],
    enabled: !MOCK_MODE,
  });

  // --- DATA SOURCE SELECTION ---
  const displayedPurchases = MOCK_MODE ? mockPurchases : purchases;
  const displayedSuppliers = MOCK_MODE ? mockSuppliers : suppliers;

  const formatCurrency = (amount) =>
    new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(Number(amount));

  const formatDate = (date) =>
    new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(date));

  const getSupplierName = (supplierId) => {
    const supplier = displayedSuppliers.find((s) => s.id === supplierId);
    return supplier?.name || "Unknown Supplier";
  };

  if (!MOCK_MODE && isLoading) {
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
        <h1 className="text-2xl font-semibold text-gray-800">Purchase Management</h1>
        <Button onClick={() => setIsAddModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Purchase
        </Button>
      </div>

      {/* Purchases Table */}
      <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="bg-gray-50">
                <TableHead>Purchase ID</TableHead>
                <TableHead>Supplier</TableHead>
                <TableHead>Total Cost</TableHead>
                <TableHead>Purchase Date</TableHead>
                <TableHead>Notes</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {displayedPurchases.length > 0 ? (
                displayedPurchases.map((purchase) => (
                  <TableRow key={purchase.id} className="hover:bg-gray-50">
                    <TableCell className="font-medium">#{purchase.id}</TableCell>
                    <TableCell>{getSupplierName(purchase.supplierId)}</TableCell>
                    <TableCell>{formatCurrency(purchase.totalCost)}</TableCell>
                    <TableCell>{formatDate(purchase.purchaseDate)}</TableCell>
                    <TableCell>{purchase.notes || "N/A"}</TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setEditingPurchase(purchase)}
                      >
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                    No purchases found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </Card>

      {/* Modals */}
      <AddPurchaseModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
      />

      {editingPurchase && (
        <EditPurchaseModal
          purchase={editingPurchase}
          isOpen={!!editingPurchase}
          onClose={() => setEditingPurchase(null)}
        />
      )}
    </div>
  );
}
