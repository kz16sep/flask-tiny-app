// Lấy tất cả các checkbox và nút xóa
const checkboxes = document.querySelectorAll('input[type="checkbox"]');
const deleteButton = document.querySelector('.btn-danger');

// Thêm sự kiện click cho nút xóa
deleteButton.addEventListener('click', async () => {
    // Lấy tất cả checkbox được chọn
    const checkedBoxes = Array.from(checkboxes).filter(cb => cb.checked && cb.id !== 'deleteAll');
    
    // Nếu không có checkbox nào được chọn thì return
    if (checkedBoxes.length === 0) return;

    // Xóa từng task được chọn
    for (const checkbox of checkedBoxes) {
        const taskId = checkbox.id.split('_')[1];
        try {
            const response = await fetch(`/delete/${taskId}`);
            if (response.ok) {
                // Nếu xóa thành công, xóa phần tử khỏi DOM
                checkbox.closest('li').remove();
            }
        } catch (error) {
            console.error('Lỗi khi xóa task:', error);
        }
    }
});

// Xử lý checkbox "Chọn tất cả"
const deleteAllCheckbox = document.getElementById('deleteAll');
deleteAllCheckbox.addEventListener('change', () => {
    checkboxes.forEach(checkbox => {
        if (checkbox.id !== 'deleteAll') {
            checkbox.checked = deleteAllCheckbox.checked;
        }
    });
});

// Hàm mở modal chỉnh sửa
function openEditModal(taskId, content) {
    const modal = new bootstrap.Modal(document.getElementById('editModal'));
    document.getElementById('taskId').value = taskId;
    document.getElementById('editTaskContent').value = content;
    modal.show();
}
