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
import ViewPurchaseModal from "@/components/purchases/view-purchase-modal";
import { BASE_URL } from "@/lib/constants";

export default function Purchases() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [viewingPurchase, setViewingPurchase] = useState(null);
  const [viewingLoading, setViewingLoading] = useState(false);
  const [currentlyViewingId, setCurrentlyViewingId] = useState(null);

  // Fetch list of purchases (basic info)
  const {
    data: purchases = [],
    isLoading: loadingPurchases,
    isError: errorPurchases,
    error: purchasesError,
  } = useQuery({
    queryKey: [`${BASE_URL}/purchases`],
    queryFn: async () => {
      const res = await fetch(`${BASE_URL}/purchases`);
      if (!res.ok) throw new Error("Failed to fetch purchases");
      return res.json();
    },
  });

  // Helper: Fetch full purchase (with items + product info)
  const fetchPurchaseDetails = async (purchaseId) => {
    setViewingLoading(true);
    setCurrentlyViewingId(purchaseId);
    try {
      const res = await fetch(`${BASE_URL}/purchases/${purchaseId}`);
      if (!res.ok) throw new Error("Failed to fetch purchase details");
      const data = await res.json();
      setViewingPurchase(data);
    } catch (err) {
      console.error("Error fetching purchase details:", err);
    } finally {
      setViewingLoading(false);
      setCurrentlyViewingId(null);
    }
  };

  // Helpers
  const formatCurrency = (amount) => {
    const parsed = parseFloat(amount);
    if (isNaN(parsed)) return "ksh0.00";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "ksh",
    }).format(parsed);
  };

  const formatDate = (date) => {
    const parsedDate = new Date(date);
    if (isNaN(parsedDate.getTime())) return "Invalid Date";
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(parsedDate);
  };

  // Loading state
  if (loadingPurchases) {
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

  // Error state
  if (errorPurchases) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-6 text-red-500">
            Error loading purchases: {purchasesError?.message || "Unknown error"}
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
              {purchases.length > 0 ? (
                purchases.map((purchase) => (
                  <TableRow key={purchase.id} className="hover:bg-gray-50">
                    <TableCell className="font-medium">#{purchase.id}</TableCell>
                    <TableCell>
                      {purchase.supplier?.name || "Unknown Supplier"}
                    </TableCell>
                    <TableCell>{formatCurrency(purchase.total_cost)}</TableCell>
                    <TableCell>{formatDate(purchase.purchase_date)}</TableCell>
                    <TableCell>{purchase.notes || "N/A"}</TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => fetchPurchaseDetails(purchase.id)}
                        disabled={viewingLoading && currentlyViewingId === purchase.id}
                      >
                        {viewingLoading && currentlyViewingId === purchase.id
                          ? "Loading..."
                          : "View Details"}
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

      {viewingPurchase && (
        <ViewPurchaseModal
          isOpen={!!viewingPurchase}
          onClose={() => setViewingPurchase(null)}
          purchase={viewingPurchase}
        />
      )}
    </div>
  );
}
