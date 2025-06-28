import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Edit, Trash2, Plus } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { BASE_URL } from "@/lib/constants";

import AddCategoryModal from "@/components/categories/add-category-modal";
import EditCategoryModal from "@/components/categories/edit-category-modal";
import DeleteCategoryModal from "@/components/categories/delete-category-modal"; 

export default function Categories() {
  const { toast } = useToast();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

  const {
    data: categories = [],
    isLoading,
    isError,
    error,
    refetch, 
  } = useQuery({
    queryKey: ["categories"],
    queryFn: async () => {
      const res = await fetch(`${BASE_URL}/categories`);
      if (!res.ok) throw new Error("Failed to fetch categories");
      return await res.json();
    },
  });

  const filteredCategories = categories.filter((category) =>
    category.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleEdit = (category) => {
    setSelectedCategory(category);
    setIsEditModalOpen(true);
  };

  // Define handleDelete here
  const handleDelete = (category) => {
    setSelectedCategory(category);
    setIsDeleteModalOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!selectedCategory || !selectedCategory.id) {
      console.error("No category selected for deletion or ID is missing.");
      toast({
        title: "Error!",
        description: "No category selected for deletion.",
        variant: "destructive",
      });
      return;
    }

    const categoryIdToDelete = selectedCategory.id;
    console.log("Attempting to send DELETE request for ID:", categoryIdToDelete);

    try {
      const response = await fetch(`${BASE_URL}/categories/${categoryIdToDelete}`, { // Use BASE_URL
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          // Add any necessary authentication tokens here, e.g., "Authorization": `Bearer ${token}`
        },
      });

      if (response.ok) {
        console.log("Category soft-deleted successfully on the backend.");
        setIsDeleteModalOpen(false); // Close the modal
        setSelectedCategory(null); // Clear selected category
        refetch(); // Use refetch to update the categories list
        toast({
          title: "Success!",
          description: "Category soft-deleted successfully.",
          variant: "default",
        });
      } else {
        const errorData = await response.json();
        console.error("Failed to soft-delete category:", errorData.error || response.statusText);
        toast({
          title: "Error!",
          description: errorData.error || "Failed to soft-delete category.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Network error during delete operation:", error);
      toast({
        title: "Error!",
        description: "Network error during delete operation.",
        variant: "destructive",
      });
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (isError) {
    return (
      <div className="text-red-500">
        Error loading categories: {error?.message || "Unknown error"}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-800">Categories</h1>
        <Button onClick={() => setIsAddModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" /> Add Category
        </Button>
      </div>

      <Input
        placeholder="Search categories..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="my-4"
      />

      <div className="p-4 bg-white rounded-lg shadow-md border border-gray-200">
        <Table>
          <TableHeader>
            <TableRow className="bg-gray-50">
              <TableHead>Category Name</TableHead>
              <TableHead>Description</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredCategories.length > 0 ? (
              filteredCategories.map((category) => (
                <TableRow key={category.id} className="hover:bg-gray-50">
                  <TableCell>{category.name}</TableCell>
                  <TableCell>{category.description}</TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEdit(category)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(category)} // This line (or similar) was causing the error
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={3} className="text-center py-8 text-gray-500">
                  No categories found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <AddCategoryModal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} />
      <EditCategoryModal
        category={selectedCategory}
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
      />

      <DeleteCategoryModal
        category={selectedCategory}
        isOpen={isDeleteModalOpen}
        onConfirm={handleConfirmDelete} // Pass the function to execute the delete API call
        onClose={() => { // Changed from 'onCancel' to 'onClose' for consistency, adjust modal prop name if needed
          setIsDeleteModalOpen(false);
          setSelectedCategory(null);
        }}
      />
    </div>
  );
}