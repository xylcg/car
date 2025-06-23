// 页面加载动画
document.addEventListener('DOMContentLoaded', function() {
    // 为所有内容添加淡入效果
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }

    // 表单提交时的加载动画
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;

                // 创建加载动画
                const loader = document.createElement('div');
                loader.className = 'loader';
                this.appendChild(loader);
                loader.style.display = 'block';

                // 模拟加载延迟（实际应用中不需要）
                if (window.location.href.includes('localhost')) {
                    setTimeout(() => {
                        loader.style.display = 'none';
                        submitBtn.disabled = false;
                    }, 1500);
                }
            }
        });
    });

    // 表格行点击效果
    const tableRows = document.querySelectorAll('table tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function() {
            // 移除之前的高亮行
            document.querySelectorAll('tr.highlight').forEach(el => {
                el.classList.remove('highlight');
            });

            // 添加高亮效果
            this.classList.add('highlight');

            // 添加脉冲动画
            this.classList.add('pulse');
            setTimeout(() => {
                this.classList.remove('pulse');
            }, 2000);
        });
    });

    // 输入框标签动画
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        const input = group.querySelector('input, select, textarea');
        const label = group.querySelector('label');

        if (input && label) {
            // 当输入框获得焦点时
            input.addEventListener('focus', function() {
                label.style.transform = 'translateY(-20px)';
                label.style.fontSize = '12px';
                label.style.color = '#3498db';
            });

            // 当输入框失去焦点时
            input.addEventListener('blur', function() {
                if (!this.value) {
                    label.style.transform = '';
                    label.style.fontSize = '';
                    label.style.color = '';
                }
            });

            // 如果输入框已经有值，初始化时也应用样式
            if (input.value) {
                label.style.transform = 'translateY(-20px)';
                label.style.fontSize = '12px';
                label.style.color = '#3498db';
            }
        }
    });
});

// 通知消息关闭功能
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // 添加关闭按钮
        const closeBtn = document.createElement('span');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.cssText = `
            position: absolute;
            right: 10px;
            top: 10px;
            cursor: pointer;
            font-size: 1.2rem;
        `;
        closeBtn.addEventListener('click', function() {
            alert.style.animation = 'fadeOut 0.5s ease-out forwards';
            setTimeout(() => {
                alert.remove();
            }, 500);
        });
        alert.appendChild(closeBtn);
    });
});