import { useState, useRef } from "react";
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
import PrintPurchaseModal from "@/components/purchases/print-purchase-modal";
import { BASE_URL } from "@/lib/constants";
import { useToast } from "@/hooks/use-toast";
import { useReactToPrint } from "react-to-print";

export default function Purchases() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [viewingPurchase, setViewingPurchase] = useState(null);
  const [viewingLoading, setViewingLoading] = useState(false);
  const [currentlyViewingId, setCurrentlyViewingId] = useState(null);

  const [sortBy, setSortBy] = useState("purchase_date");
  const [sortDirection, setSortDirection] = useState("desc");

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const { toast } = useToast();
  const printRef = useRef();

  const handlePrint = useReactToPrint({
    content: () => printRef.current,
    documentTitle: `Purchase-${viewingPurchase?.id || "unknown"}`,
    removeAfterPrint: true,
  });

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
      toast({
        title: "Fetch error",
        description: err.message,
        variant: "destructive",
      });
    } finally {
      setViewingLoading(false);
      setCurrentlyViewingId(null);
    }
  };

  const formatCurrency = (amount) => {
    const parsed = parseFloat(amount);
    if (isNaN(parsed)) return "ksh0.00";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "KES",
    }).format(parsed);
  };

  const formatDate = (date) => {
    const parsedDate = new Date(date);
    if (isNaN(parsedDate.getTime())) return "Invalid Date";
    return new Intl.DateTimeFormat("en-KE", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(parsedDate);
  };

  const handleSort = (key) => {
    if (sortBy === key) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortBy(key);
      setSortDirection("asc");
    }
  };

  const filteredPurchases = purchases.filter((purchase) => {
    const purchaseDate = new Date(purchase.purchase_date);
    const from = startDate ? new Date(startDate) : null;
    const to = endDate ? new Date(endDate) : null;

    if (from && purchaseDate < from) return false;
    if (to && purchaseDate > to) return false;
    return true;
  });

  const sortedPurchases = [...filteredPurchases].sort((a, b) => {
    let valueA, valueB;

    switch (sortBy) {
      case "id":
        valueA = a.id;
        valueB = b.id;
        break;
      case "total_cost":
        valueA = parseFloat(a.total_cost);
        valueB = parseFloat(b.total_cost);
        break;
      case "purchase_date":
        valueA = new Date(a.purchase_date).getTime();
        valueB = new Date(b.purchase_date).getTime();
        break;
      default:
        return 0;
    }

    return sortDirection === "asc"
      ? valueA > valueB ? 1 : valueA < valueB ? -1 : 0
      : valueA < valueB ? 1 : valueA > valueB ? -1 : 0;
  });

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
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h1 className="text-2xl font-semibold text-gray-800">Purchase Management</h1>
        <div className="flex flex-wrap gap-3 items-center">
          <div className="flex gap-2">
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="border rounded px-2 py-1 text-sm"
              placeholder="From"
            />
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="border rounded px-2 py-1 text-sm"
              placeholder="To"
            />
          </div>
          <Button onClick={() => setIsAddModalOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Purchase
          </Button>
        </div>
      </div>

      <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="bg-gray-50">
                <TableHead onClick={() => handleSort("id")} className="cursor-pointer select-none">
                  Purchase ID {sortBy === "id" ? (sortDirection === "asc" ? "↑" : "↓") : ""}
                </TableHead>
                <TableHead>Supplier</TableHead>
                <TableHead onClick={() => handleSort("total_cost")} className="cursor-pointer select-none">
                  Total Cost {sortBy === "total_cost" ? (sortDirection === "asc" ? "↑" : "↓") : ""}
                </TableHead>
                <TableHead onClick={() => handleSort("purchase_date")} className="cursor-pointer select-none">
                  Purchase Date {sortBy === "purchase_date" ? (sortDirection === "asc" ? "↑" : "↓") : ""}
                </TableHead>
                <TableHead>Notes</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedPurchases.length > 0 ? (
                sortedPurchases.map((purchase) => (
                  <TableRow
                    key={purchase.id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => fetchPurchaseDetails(purchase.id)}
                  >
                    <TableCell className="font-medium">#{purchase.id}</TableCell>
                    <TableCell>{purchase.supplier?.name || "Unknown Supplier"}</TableCell>
                    <TableCell>{formatCurrency(purchase.total_cost)}</TableCell>
                    <TableCell>{formatDate(purchase.purchase_date)}</TableCell>
                    <TableCell>{purchase.notes || "N/A"}</TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          fetchPurchaseDetails(purchase.id);
                        }}
                        disabled={viewingLoading && currentlyViewingId === purchase.id}
                      >
                        {viewingLoading && currentlyViewingId === purchase.id ? "Loading..." : "View Details"}
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

      <AddPurchaseModal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} />

      {viewingPurchase && (
        <ViewPurchaseModal
          isOpen={!!viewingPurchase}
          onClose={() => setViewingPurchase(null)}
          purchase={viewingPurchase}
          onPrint={handlePrint}
        />
      )}

      <PrintPurchaseModal ref={printRef} purchase={viewingPurchase} />
    </div>
  );
}
