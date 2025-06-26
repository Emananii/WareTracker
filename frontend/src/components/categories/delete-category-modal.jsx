import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useMutation } from "@tanstack/react-query";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import {BASE_URL} from "@/lib/constants"; 


export default function DeleteCategoryModal({ category, isOpen, onClose }) {
  const { toast } = useToast();

  

  // Mutation for deleting the category
  const deleteCategoryMutation = useMutation({
    mutationFn: async (id) => {
  return apiRequest("DELETE", `${BASE_URL}categories/${id}`);
},
     onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/categories"] }); // Invalidate cached categories data
      toast({
        title: "Category Deleted",
        description: "Category has been deleted successfully", // Toast message on success
      });
      onClose(); // Close modal after success
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message || "Something went wrong", // Toast message on error
        variant: "destructive",
      });
    },
  });

  // Handle deletion when the user confirms
  const handleDelete = () => {
    if (category?.id) {
      deleteCategoryMutation.mutate(category.id); // Trigger the mutation with category ID
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold text-gray-800">Delete Category</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <p>Are you sure you want to delete the category "{category?.name}"?</p>
          <div className="flex space-x-3 pt-4">
            <Button variant="outline" className="flex-1" onClick={onClose}>Cancel</Button>
            <Button variant="destructive" className="flex-1" onClick={handleDelete}>Delete</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
