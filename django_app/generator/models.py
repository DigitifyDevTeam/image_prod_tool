from django.db import models


class BatchSubmission(models.Model):
    """Model to group multiple product submissions together"""
    # Vertical picto positions (shared across all images in batch)
    vertical_pos_1 = models.CharField(max_length=255, null=True, blank=True)
    vertical_pos_2 = models.CharField(max_length=255, null=True, blank=True)
    vertical_pos_3 = models.CharField(max_length=255, null=True, blank=True)
    vertical_pos_4 = models.CharField(max_length=255, null=True, blank=True)
    vertical_pos_5 = models.CharField(max_length=255, null=True, blank=True)
    
    # Horizontal picto positions (shared across all images in batch)
    horizontal_cat_1 = models.CharField(max_length=255, null=True, blank=True)
    horizontal_file_1 = models.CharField(max_length=255, null=True, blank=True)
    horizontal_cat_2 = models.CharField(max_length=255, null=True, blank=True)
    horizontal_file_2 = models.CharField(max_length=255, null=True, blank=True)
    horizontal_cat_3 = models.CharField(max_length=255, null=True, blank=True)
    horizontal_file_3 = models.CharField(max_length=255, null=True, blank=True)
    horizontal_cat_4 = models.CharField(max_length=255, null=True, blank=True)
    horizontal_file_4 = models.CharField(max_length=255, null=True, blank=True)
    horizontal_cat_5 = models.CharField(max_length=255, null=True, blank=True)
    horizontal_file_5 = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Batch {self.id} - {self.created_at}"


class ProductSubmission(models.Model):
    """Model to store individual product submissions and their results"""
    batch = models.ForeignKey(BatchSubmission, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    product_image = models.ImageField(upload_to='products/')
    result_image = models.ImageField(upload_to='results/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Product {self.id} - {self.created_at}"
