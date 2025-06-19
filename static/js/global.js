    document.addEventListener('DOMContentLoaded', function() {
        // Função para ler o valor de um cookie específico
        function getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
        }

        // Função para alterar o idioma
        function changeLanguage(lang) {
            // O cookie 'googtrans' informa ao Google para qual idioma traduzir.
            // O formato é /idioma_origem/idioma_destino
            document.cookie = `googtrans=/auto/${lang}; path=/`;
            // Recarrega a página para que a tradução seja aplicada
            window.location.reload();
        }

        // Adiciona os eventos de clique aos botões de idioma
        const btnPT = document.getElementById('translate-pt');
        const btnEN = document.getElementById('translate-en');

        if (btnPT) {
            btnPT.addEventListener('click', function(e) {
                e.preventDefault();
                // Define o idioma para português (ou remove a tradução)
                changeLanguage('pt');
            });
        }

        if (btnEN) {
            btnEN.addEventListener('click', function(e) {
                e.preventDefault();
                // Define o idioma para inglês
                changeLanguage('en');
            });
        }

        // Função para destacar o botão do idioma ativo
        function setActiveLanguageButton() {
            const langCookie = getCookie('googtrans');
            
            // Remove a classe ativa de ambos os botões primeiro
            btnPT.classList.remove('bg-indigo-600', 'text-white');
            btnEN.classList.remove('bg-indigo-600', 'text-white');
            
            // Adiciona a classe de volta ao estilo padrão
            btnPT.classList.add('bg-gray-700', 'text-gray-300', 'hover:bg-gray-600');
            btnEN.classList.add('bg-gray-700', 'text-gray-300', 'hover:bg-gray-600');

            if (langCookie && langCookie.includes('/en')) {
                // Se o idioma for inglês, destaca o botão EN
                btnEN.classList.add('bg-indigo-600', 'text-white');
                btnEN.classList.remove('bg-gray-700', 'text-gray-300', 'hover:bg-gray-600');
            } else {
                // Caso contrário (português ou sem cookie), destaca o botão PT
                btnPT.classList.add('bg-indigo-600', 'text-white');
                btnPT.classList.remove('bg-gray-700', 'text-gray-300', 'hover:bg-gray-600');
            }
        }

        // Chama a função para definir o botão ativo assim que a página carregar
        if (btnPT && btnEN) {
            setActiveLanguageButton();
        }
    });