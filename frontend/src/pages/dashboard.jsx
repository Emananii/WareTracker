import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import {
  Package,
  AlertTriangle,
  DollarSign,
  Truck,
  ArrowRight,
  ArrowDown,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function Dashboard() {
  const { data: stats = {}, isLoading } = useQuery({
    queryKey: ["/api/dashboard/stats"],
  });

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  const formatTimeAgo = (date) => {
    const now = new Date();
    const then = new Date(date);
    const diffInHours = Math.floor((now - then) / (1000 * 60 * 60));
    if (diffInHours < 1) return "Just now";
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    return `${Math.floor(diffInHours / 24)} days ago`;
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-20 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Items */}
        <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Total Items</p>
                <p className="text-3xl font-semibold text-gray-900">
                  {stats.totalItems?.toLocaleString() || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Package className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className="text-green-600 text-sm font-medium">Active</span>
              <span className="text-gray-500 text-sm ml-2">inventory items</span>
            </div>
          </CardContent>
        </Card>

        {/* Low Stock */}
        <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Low Stock</p>
                <p className="text-3xl font-semibold text-gray-900">
                  {stats.lowStockCount || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className="text-red-600 text-sm font-medium">Critical</span>
              <span className="text-gray-500 text-sm ml-2">requires attention</span>
            </div>
          </CardContent>
        </Card>

        {/* Monthly Purchases */}
        <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Monthly Purchases</p>
                <p className="text-3xl font-semibold text-gray-900">
                  {formatCurrency(stats.monthlyPurchases || 0)}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className="text-green-600 text-sm font-medium">This month</span>
            </div>
          </CardContent>
        </Card>

        {/* Today’s Movements */}
        <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Movements Today</p>
                <p className="text-3xl font-semibold text-gray-900">
                  {stats.todayMovements || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Truck className="h-6 w-6 text-orange-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className="text-gray-500 text-sm">Active transfers</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity & Low Stock */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Movements */}
        <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800">Recent Movements</h3>
          </div>
          <CardContent className="p-6">
            {stats.recentMovements?.length > 0 ? (
              <div className="space-y-4">
                {stats.recentMovements.map((movement) => (
                  <div
                    key={movement.id}
                    className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0"
                  >
                    <div className="flex items-center">
                      <div
                        className={`w-10 h-10 rounded-lg flex items-center justify-center mr-3 ${
                          movement.type === "out_to_business"
                            ? "bg-blue-100"
                            : movement.type === "in_from_business"
                            ? "bg-green-100"
                            : "bg-orange-100"
                        }`}
                      >
                        {movement.type === "out_to_business" && (
                          <ArrowRight className="h-5 w-5 text-blue-600" />
                        )}
                        {movement.type === "in_from_business" && (
                          <ArrowDown className="h-5 w-5 text-green-600" />
                        )}
                        {movement.type === "adjustment" && (
                          <Package className="h-5 w-5 text-orange-600" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">
                          {movement.type === "out_to_business"
                            ? "Transfer to Business"
                            : movement.type === "in_from_business"
                            ? "Return from Business"
                            : "Inventory Adjustment"}
                        </p>
                        <p className="text-sm text-gray-500">
                          Qty: {movement.quantity}
                        </p>
                      </div>
                    </div>
                    <span className="text-sm text-gray-500">
                      {formatTimeAgo(movement.movementDate)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No recent movements</p>
            )}
          </CardContent>
        </Card>

        {/* Low Stock Alerts */}
        <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800">Low Stock Alerts</h3>
          </div>
          <CardContent className="p-6">
            {stats.lowStockItems?.length > 0 ? (
              <div className="space-y-4">
                {stats.lowStockItems.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0"
                  >
                    <div className="flex items-center">
                      <div
                        className={`w-10 h-10 rounded-lg flex items-center justify-center mr-3 ${
                          item.quantity === 0
                            ? "bg-red-100"
                            : item.quantity <= 5
                            ? "bg-red-100"
                            : "bg-yellow-100"
                        }`}
                      >
                        <AlertTriangle
                          className={`h-5 w-5 ${
                            item.quantity === 0
                              ? "text-red-600"
                              : item.quantity <= 5
                              ? "text-red-600"
                              : "text-yellow-600"
                          }`}
                        />
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">{item.name}</p>
                        <p className="text-sm text-gray-500">
                          SKU: {item.sku} • Location: {item.location || "N/A"}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span
                        className={`font-medium text-sm ${
                          item.quantity === 0
                            ? "text-red-600"
                            : item.quantity <= 5
                            ? "text-red-600"
                            : "text-yellow-600"
                        }`}
                      >
                        {item.quantity} left
                      </span>
                      <p className="text-xs text-gray-500">
                        Min: {item.minStock || 0}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No low stock items</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}