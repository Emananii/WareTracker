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

export default function Dashboard() {
  const { data: stats = {}, isLoading } = useQuery({
    queryKey: ["/dashboard/summary"],
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
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Total Items</p>
                <p className="text-3xl font-semibold text-gray-900">
                  {stats.total_items || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Package className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-4 text-sm text-gray-500">All inventory records</div>
          </CardContent>
        </Card>

        <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Low Stock</p>
                <p className="text-3xl font-semibold text-gray-900">
                  {stats.low_stock_count || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
            </div>
            <div className="mt-4 text-sm text-red-600">Needs restocking</div>
          </CardContent>
        </Card>

        <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Out of Stock</p>
                <p className="text-3xl font-semibold text-gray-900">
                  {stats.out_of_stock_count || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                <AlertTriangle className="h-6 w-6 text-gray-600" />
              </div>
            </div>
            <div className="mt-4 text-sm text-gray-500">No units available</div>
          </CardContent>
        </Card>

        <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Total Stock</p>
                <p className="text-3xl font-semibold text-gray-900">
                  {stats.total_stock || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Package className="h-6 w-6 text-green-600" />
              </div>
            </div>
            <div className="mt-4 text-sm text-green-600">Available quantity</div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 gap-6">
        <Card className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800">Recent Activity</h3>
          </div>
          <CardContent className="p-6 space-y-6">
            <div>
              <h4 className="text-sm font-medium text-gray-600 mb-2">Recent Purchases</h4>
              {stats.recent_purchases?.length > 0 ? (
                <ul className="space-y-2">
                  {stats.recent_purchases.map((purchase) => (
                    <li key={purchase.id} className="flex justify-between border-b pb-2">
                      <span className="text-gray-800">{purchase.notes}</span>
                      <span className="text-sm text-gray-500">
                        {formatTimeAgo(purchase.purchase_date)}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500">No recent purchases</p>
              )}
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-600 mb-2">Recent Transfers</h4>
              {stats.recent_transfers?.length > 0 ? (
                <ul className="space-y-2">
                  {stats.recent_transfers.map((transfer) => (
                    <li key={transfer.id} className="flex justify-between border-b pb-2">
                      <span className="text-gray-800">{transfer.notes}</span>
                      <span className="text-sm text-gray-500">
                        {formatTimeAgo(transfer.date)}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500">No recent transfers</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
