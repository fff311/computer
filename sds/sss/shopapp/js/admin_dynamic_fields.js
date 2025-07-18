document.addEventListener('DOMContentLoaded', function () {
    const conditionField = document.querySelector('#id_condition');
    const slopeStateField = document.querySelector('#id_slope_state').closest('.form-row');
    const signImageField = document.querySelector('#id_sign_image').closest('.form-row');

    function toggleFields() {
        const conditionValue = conditionField.value;

        if (conditionValue === 'ограниченный доступ') {
            slopeStateField.style.display = '';
            const slopeStateValue = document.querySelector('#id_slope_state').value;
            if (slopeStateValue === 'по знаку') {
                signImageField.style.display = '';
            } else {
                signImageField.style.display = 'none';
            }
        } else {
            slopeStateField.style.display = 'none';
            signImageField.style.display = 'none';
        }
    }

    // Скрываем поля по умолчанию
    toggleFields();

    // Добавляем обработчики событий для динамического отображения
    conditionField.addEventListener('change', toggleFields);
    document.querySelector('#id_slope_state').addEventListener('change', toggleFields);
});