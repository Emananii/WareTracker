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
import AddStockTransferModal from "@/components/stock-transfers/add-stock-transfer-modal";
import { BASE_URL } from "@/lib/constants"; // ✅ if you’re using a base path

export default function StockTransfers() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // ✅ Fetch all stock transfers
  const { data: transfers = [], isLoading } = useQuery({
    queryKey: ["stock_transfers"],
    queryFn: async () => {
      const res = await fetch(`${BASE_URL}/stock_transfers`);
      if (!res.ok) throw new Error("Failed to fetch stock transfers");
      return res.json();
    },
  });

  // ✅ Fetch businesses (locations)
  const { data: businesses = [] } = useQuery({
    queryKey: ["business_locations"],
    queryFn: async () => {
      const res = await fetch(`${BASE_URL}/business_locations`);
      if (!res.ok) throw new Error("Failed to fetch business locations");
      return res.json();
    },
  });

  // ✅ Format date into a readable string
  const formatDate = (date) => {
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(date));
  };

  // ✅ Lookup location name
  const getLocationName = (id) => {
    const location = businesses.find((b) => b.id === id);
    return location?.name || "Unknown";
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
        <h1 className="text-2xl font-semibold text-gray-800">Stock Transfers</h1>
        <Button onClick={() => setIsAddModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Transfer
        </Button>
      </div>

      {/* Transfers Table */}
      <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="bg-gray-50">
                <TableHead>ID</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Notes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transfers.length > 0 ? (
                transfers.map((transfer) => (
                  <TableRow key={transfer.id} className="hover:bg-gray-50">
                    <TableCell>{transfer.id}</TableCell>
                    <TableCell>{formatDate(transfer.date)}</TableCell>
                    <TableCell>{getLocationName(transfer.location_id)}</TableCell>
                    <TableCell>{transfer.notes || "-"}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-8 text-gray-500">
                    No stock transfers found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </Card>

      {/* Add Modal */}
      <AddStockTransferModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
      />
    </div>
  );
}
