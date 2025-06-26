import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Edit, Trash2, Plus, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";
import AddCategoryModal from "@/components/categories/add-category-modal";
import EditCategoryModal from "@/components/categories/edit-category-modal";
import DeleteCategoryModal from "@/components/categories/delete-category-modal";

export default function Categories() {
  const { toast } = useToast();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null); // For selected category
  const [searchTerm, setSearchTerm] = useState("");

  // Mocked data for categories
  const mockedCategories = [
    { id: 1, name: "Electronics", description: "Devices and gadgets" },
    { id: 2, name: "Groceries", description: "Food and beverages" },
    { id: 3, name: "Furniture", description: "Furniture and home decor" },
    { id: 4, name: "Toys", description: "Children's toys and games" },
  ];

  const { data: categories = mockedCategories, isLoading } = useQuery({
    queryKey: ["/api/categories"],
    queryFn: async () => {
      return mockedCategories;
    },
  });

  const handleEdit = (category) => {
    setSelectedCategory(category); // Store selected category for editing
    setIsEditModalOpen(true); // Open edit modal
  };

  const handleDelete = (category) => {
    setSelectedCategory(category); // Store selected category for deletion
    setIsDeleteModalOpen(true); // Open delete modal
  };

  // Handle search functionality
  const filteredCategories = categories.filter((category) =>
    category.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1>Categories</h1>
        <Button onClick={() => setIsAddModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" /> Add Category
        </Button>
      </div>

      {/* Search Bar */}
      <Input
        placeholder="Search categories..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="my-4" // Adding margin to give space between the search bar and the table
      />

      {/* Table Wrapper */}
      <div className="p-4 bg-white rounded-lg shadow-md border border-gray-200">
        <Table>
          <TableHeader>
            <TableRow className="bg-gray-50">
              <TableHead>Category Name</TableHead>
              <TableHead>Description</TableHead> {/* Add description column */}
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredCategories.map((category) => (
              <TableRow key={category.id} className="hover:bg-gray-50">
                <TableCell>{category.name}</TableCell>
                <TableCell>{category.description}</TableCell> {/* Display description */}
                <TableCell className="text-right">
                  <Button variant="ghost" size="sm" onClick={() => handleEdit(category)}>
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => handleDelete(category)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Modals */}
      <AddCategoryModal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} />
      <EditCategoryModal category={selectedCategory} isOpen={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} />
      <DeleteCategoryModal category={selectedCategory} isOpen={isDeleteModalOpen} onClose={() => setIsDeleteModalOpen(false)} />
    </div>
  );
}
