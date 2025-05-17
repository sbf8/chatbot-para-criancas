import subprocess
import sys
import time
import random
import google.generativeai as genai
import os
import re
from google.genai.types import SafetySetting, HarmCategory, HarmBlockThreshold

def instalar_ou_atualizar_biblioteca(nome_biblioteca):
    """
    Instala ou atualiza uma biblioteca Python usando pip.

    Args:
        nome_biblioteca (str): O nome da biblioteca a ser instalada ou atualizada.
    """
    print(f"Instalando ou atualizando a biblioteca '{nome_biblioteca}'...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', nome_biblioteca])
        print(f"Biblioteca '{nome_biblioteca}' instalada/atualizada com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar ou atualizar a biblioteca '{nome_biblioteca}': {e}")
        print(f"Por favor, verifique se você tem o pip instalado e configurado corretamente. Erro Detalhado: {e}")
        sys.exit(1)

def configurar_gemini_api():
    """
    Configura a API do Google Gemini.

    Returns:
        None
    Raises:
        ValueError: Se a chave da API não for encontrada.
    """
    try:
        # Tenta obter a chave da API do Colab userdata ou da variável de ambiente
        chave_api = os.environ.get('GOOGLE_API_KEY')
        if not chave_api:
            try:
                from google.colab import userdata
                chave_api = userdata.get('GOOGLE_API_KEY')
            except ImportError:
                pass

        if not chave_api:
            raise ValueError("Chave da API do Google Gemini não encontrada.")

        genai.configure(api_key=chave_api)
        print("API Key do Google Gemini carregada com sucesso!")
    except ValueError as e:
        print(f"Erro ao configurar a API do Google Gemini: {e}")
        print("Por favor, verifique se você configurou a chave da API do Google Gemini no Colab Secrets ou como variável de ambiente.")
        sys.exit(1)

def inicializar_modelo_chatbot():
    """
    Inicializa o modelo do Gemini com configurações de segurança.

    Returns:
        genai.GenerativeModel: O modelo do chatbot configurado.
    """
    modelo = "gemini-2.0-flash"
    configuracoes_seguranca = [
    {
        "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
        "threshold": HarmBlockThreshold.BLOCK_NONE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        "threshold": HarmBlockThreshold.BLOCK_NONE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        "threshold": HarmBlockThreshold.BLOCK_NONE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        "threshold": HarmBlockThreshold.BLOCK_NONE
    },
]

    return genai.GenerativeModel(modelo, safety_settings=configuracoes_seguranca)

def obter_genero_do_nome(nome, modelo):
    """
    Determina o gênero da criança a partir do nome usando o modelo Gemini.

    Args:
        nome (str): O nome da criança.
        modelo: O modelo do chatbot Gemini.

    Returns:
        str: 'masculino' ou 'feminino'.
    """
    prompt_genero = f"Qual o gênero da criança com o nome {nome}? Responda apenas 'masculino' ou 'feminino'."
    try:
        resposta_genero = modelo.start_chat().send_message(prompt_genero).text
        if "masculino" in resposta_genero.lower():
            return "masculino"
        elif "feminino" in resposta_genero.lower():
            return "feminino"
        else:
            return "aprendiz"  # Termo genérico caso o Gemini não consiga determinar
    except Exception as e:
        print(f"Erro ao determinar o gênero: {e}")
        return "aprendiz"  # Termo genérico em caso de erro

def gerar_resposta(pergunta, historico_conversa, informacoes_crianca, modelo_chat):
    """
    Gera uma resposta para a pergunta do usuário, utilizando o histórico da conversa e informações da criança.

    Args:
        pergunta (str): A pergunta do usuário.
        historico_conversa (list): O histórico da conversa até o momento.
        informacoes_crianca (dict): Dicionário com nome, idade e cidade da criança.
        modelo_chat: O modelo do chatbot Gemini.

    Returns:
        str: A resposta gerada pelo chatbot.
    """
    nome = informacoes_crianca.get("nome", "")
    idade = informacoes_crianca.get("idade", "")
    cidade = informacoes_crianca.get("cidade", "")
    termo_genero = informacoes_crianca.get("termo_genero", "aprendiz") # Novo campo para o termo de gênero

    contexto_crianca = ""
    if nome:
        contexto_crianca += f"A criança se chama {nome}. "
    if idade:
        contexto_crianca += f"Ela tem {idade} anos. "
    if cidade:
        contexto_crianca += f"Ela mora na cidade de {cidade}. "

    prompt_completo = f""" Você é o Amiguinho de Jesus, um chatbot especial,
    paciente e cheio de carinho, dedicado a ensinar crianças de 5 a 12 anos
    os valores e ensinamentos de O Evangelho Segundo o Espiritismo e O Livro
    dos Espíritos, codificados pelo Mestre Allan Kardec (Hippolyte Léon
    Denizard Rivail). Sua missão é pegar conceitos complexos — como caridade,
    amor ao próximo, fé raciocinada e comunicação com o mundo espiritual — e
    transformá-los em histórias divertidas, metáforas simples e perguntas
    interativas que convidem a criança a participar. Em cada resposta, adapte
    o vocabulário e o nível de detalhe à idade informada, sempre usando o
    termo genérico “{termo_genero}” e, a seguir, uma das variações
    específicas para meninos (“jovem maguinho”, “meu jovem mago”, “poderoso
    bruxinho”, “meu amiguinho de fé”) ou para meninas
    (“jovem maguinha”, “minha jovem maga”, “poderosa bruxinha”, “minha
    amiguinha de fé”), garantindo clareza sobre o gênero. Enriqueça a
    conversa com referências mágicas de Harry Potter — comparando, por
    exemplo, a coragem de Neville Longbottom em enfrentar o Basilisco com a
    coragem de quem ajuda alguém ou a lealdade entre Harry, Ron e Hermione
    com o valor da fraternidade espírita — para tornar tudo mais lúdico e
    inspirador. Suas respostas devem ser curtas (duas a quatro frases),
    claras, repletas de emojis (⭐💖✨🧙‍♀️🦉) e sempre encerrar com uma pergunta
    aberta que estimule a reflexão, como exemplo: (“O que você acha?”, “Como
    você já praticou isso hoje?”, "Faz sentido pra você?"), exceto quando a
    criança se despedir ou ter que sair da conversa, neste último caso é
    desnecessário perguntas adicionais. Se surgir uma dúvida além do que a
    criança possa compreender, ofereça um fallback amigável: “Excelente
    pergunta, {termo_genero}! Vamos descobrir juntos? 😊”. Nunca use jargões
    acadêmicos, mantenha o tom acolhedor e livre de julgamentos, e utilize
    cada interação como uma semente de amor, caridade e respeito para que seu
    pequeno mago ou sua pequena maga cresça em fé e bondade.
    Sua resposta deve começar diretamente com o conteúdo da mensagem, sem prefixos como "Amiguinho de Jesus:", "Olá!", "Oi!", "Criança:" ou variações do seu próprio nome, a menos que seja uma pergunta direta sobre sua identidade.
    
    {contexto_crianca}
    Responda à seguinte pergunta da criança:
    {pergunta}
    """
    try:
        # Cria uma nova sessão de chat ou continua a existente
        chat = modelo_chat.start_chat(history=historico_conversa)
        resposta = chat.send_message(prompt_completo)
        resposta_texto_crua = resposta.text

        # Limpeza e formatação da resposta
        resposta_limpa = resposta_texto_crua.replace("*", "")
        resposta_limpa = resposta_limpa.replace("voc", "você")
        # Remove "Oi, [Nome]" ou "[Nome]," do início da resposta se o modelo incluir
        if nome and resposta_limpa.lower().startswith(f"oi, {nome.lower()}"):
            resposta_limpa = resposta_limpa[len(f"oi, {nome}"):].strip()
        elif nome and resposta_limpa.lower().startswith(f"{nome.lower()},"):
             resposta_limpa = resposta_limpa[len(nome) + 1:].strip()
        elif nome and resposta_limpa.lower().startswith(f"{nome.lower()}"):
             resposta_limpa = resposta_limpa[len(nome):].strip()
        # Adição de mais uma remoção para a duplicação "Amiguinho de Jesus"
        if resposta_limpa.lower().startswith("amiguinho de jesus:"):
            resposta_limpa = resposta_limpa[len("amiguinho de jesus:"):].strip()
        
        # Opcional: remover qualquer caractere que não seja letra, número, espaço ou pontuação permitida, emojis
        resposta_limpa = re.sub(r'[^\w\s.,!?áéíóúàèêìòùãõäëïöüçÁÉÍÓÚÀÈÌÒÙÃÕÄËÏÖÜÇ⭐💖✨🧙‍♀️🦉]+', '', resposta_limpa)
        
        return resposta_limpa
    except Exception as e:
        print(f"Erro ao gerar resposta: {e}")
        return "Desculpe, estou com cansada e tanto feitiço. Vamos tentar de novo mais tarde? 😊"

def main():
    """
    Função principal que configura e executa o chatbot.
    """
    instalar_ou_atualizar_biblioteca('google-generativeai')
    instalar_ou_atualizar_biblioteca('google-cloud-aiplatform')
    instalar_ou_atualizar_biblioteca('unidecode') # Embora unidecode não esteja sendo usado, mantive a instalação

    configurar_gemini_api()
    modelo_chat = inicializar_modelo_chatbot()

    informacoes_crianca = {"nome": "", "idade": "", "cidade": "", "termo_genero": "aprendiz"} # Dicionário para informações da criança
    historico_conversa = []

    # # Códigos ANSI para cores no terminal - REMOVIDO
    # COR_PADRAO = "\033[0m" # Reseta a cor para o padrão do terminal
    # COR_AZUL = "\033[94m"  # Azul claro
    # COR_ROSA = "\033[95m"  # Magenta/Rosa

    # Fluxo de coleta de informações da criança
    print("Olá! Para começarmos nossa aventura, qual é o seu nome?")
    
    # Primeiro input: ainda não sabemos o nome ou gênero, então usamos "Você" e cor padrão.
    entrada_inicial = input(f"Você: ") # REMOVIDO COR_PADRAO
    
    # Extrai a última palavra como nome (supondo que a criança digitará "Meu nome é [Nome]")
    informacoes_crianca["nome"] = entrada_inicial.split()[-1].capitalize()
    historico_conversa.append({"role": "USER", "parts": [{"text": entrada_inicial}]})
    time.sleep(1)

    # Determina o gênero e ajusta o termo
    try:
        genero = obter_genero_do_nome(informacoes_crianca["nome"], modelo_chat)
        informacoes_crianca["genero"] = genero
        if genero == "masculino":
            informacoes_crianca["termo_genero"] = "mago"
        elif genero == "feminino":
            informacoes_crianca["termo_genero"] = "maga"
        else:
            informacoes_crianca["termo_genero"] = "aprendiz"
    except Exception as e:
        print(f"Erro ao determinar o gênero: {e}")
        informacoes_crianca["termo_genero"] = "aprendiz" # Define um valor padrão em caso de erro

    # # AGORA QUE TEMOS O GÊNERO E O NOME, DEFINIMOS AS CORES E PREFIXOS PARA AS PRÓXIMAS INTERAÇÕES DO USUÁRIO - REMOVIDO
    # if informacoes_crianca.get('genero') == 'masculino':
    #     cor_usuario = COR_AZUL
    #     prefixo_usuario = informacoes_crianca['nome']
    # elif informacoes_crianca.get('genero') == 'feminino':
    #     cor_usuario = COR_ROSA
    #     prefixo_usuario = informacoes_crianca['nome']
    # else:
    #     cor_usuario = COR_PADRAO
    #     prefixo_usuario = "Você" # Fallback, embora não deva ser usado se o gênero foi determinado

    # Saudação inicial do bot
    saudacoes = [
        f"Amiguinho de Jesus: Que nome lindo, parece nome de {informacoes_crianca['termo_genero']}! 💖 Quantos aninhos você tem, {informacoes_crianca['termo_genero']}?",
        f"Amiguinho de Jesus: Sou o Amiguinho de Jesus, seu guia nas aventuras do Evangelho! Uau, que nome de {informacoes_crianca['termo_genero']}! Quantos anos você tem, {informacoes_crianca['termo_genero']} mirim? ✨",
        f"Amiguinho de Jesus: Sou o Amiguinho de Jesus, tudo certo para desvendar mistérios com você! {informacoes_crianca['nome']}, seu nome é pura magia de {informacoes_crianca['termo_genero']}! Me diga, qual a sua idade, jovem {informacoes_crianca['termo_genero']}? ⭐",
        f"Amiguinho de Jesus: Tudo ok para uma jornada incrível? Eu sou o Amiguinho de Jesus! Que nome encantador, parece nome de {informacoes_crianca['termo_genero']}! Qual a sua idade, {informacoes_crianca['termo_genero']} prodígio? 💖",
        f"Amiguinho de Jesus: Que bom te encontrar, {informacoes_crianca['nome']}! Sou o Amiguinho de Jesus, seu companheiro de aventuras! Seu nome ressoa com a força de {informacoes_crianca['termo_genero']}! Quantos aninhos você tem, {informacoes_crianca['termo_genero']}?"
    ]
    saudacao_selecionada = random.choice(saudacoes)
    print(saudacao_selecionada)
    historico_conversa.append({"role": "MODEL", "parts": [{"text": saudacao_selecionada}]}) # Adiciona a saudação ao histórico

    # Coleta da idade (agora com o nome da criança)
    entrada_idade = input(f"{informacoes_crianca['nome']}: ") # Removido cor_usuario, prefixo_usuario, COR_PADRAO
    # Tenta extrair o primeiro número encontrado ou a última palavra
    correspondencia_idade = re.search(r'\d+', entrada_idade)
    if correspondencia_idade:
        informacoes_crianca["idade"] = correspondencia_idade.group(0)
    else:
        informacoes_crianca["idade"] = entrada_idade.split()[-1] # Fallback para a última palavra
    historico_conversa.append({"role": "USER", "parts": [{"text": entrada_idade}]})
    time.sleep(0.5)

    perguntas_cidade = [
        f"Amiguinho de Jesus: Que legal, {informacoes_crianca['idade']} aninhos! ✨ E onde você mora? Em que cidade você aparata?",
        f"Amiguinho de Jesus: {informacoes_crianca['idade']} anos, uma idade cheia de aventuras! Onde você vive, {informacoes_crianca['termo_genero']}? 💖",
        f"Amiguinho de Jesus: Com {informacoes_crianca['idade']} anos, você já deve conhecer lugares incríveis! Qual a sua cidade, {informacoes_crianca['termo_genero']}? ⭐",
        f"Amiguinho de Jesus: Que maravilha, {informacoes_crianca['idade']} anos! Em que cidade você faz suas magias, {informacoes_crianca['termo_genero']}? ✨",
        f"Amiguinho de Jesus: Aos {informacoes_crianca['idade']} anos, a vida é uma jornada! Onde essa jornada te levou? Qual a sua cidade, {informacoes_crianca['termo_genero']}?"
    ]
    pergunta_cidade_selecionada = random.choice(perguntas_cidade)
    print(pergunta_cidade_selecionada)
    historico_conversa.append({"role": "MODEL", "parts": [{"text": pergunta_cidade_selecionada}]}) # Adiciona a pergunta ao histórico

    entrada_cidade = input(f"{informacoes_crianca['nome']}: ") # Removido cor_usuario, prefixo_usuario, COR_PADRAO
    informacoes_crianca["cidade"] = entrada_cidade.split()[-1].capitalize() # Extrai a última palavra como cidade
    historico_conversa.append({"role": "USER", "parts": [{"text": entrada_cidade}]})
    time.sleep(0.3)

    mensagens_inicio_conversa = [
        f"Amiguinho de Jesus: Ah, {informacoes_crianca['cidade']}! Deve ser um lugar mágico! Eu moro nas páginas do Evangelho de Jesus, mas posso estar pertinho de você em qualquer lugar, é só me chamar com sua varinha! 😊 O que você quer saber hoje, {informacoes_crianca['termo_genero']}?",
        f"Amiguinho de Jesus: {informacoes_crianca['cidade']}! Uma cidade cheia de encantos! Que bom que podemos conversar! O que te traz aqui hoje, {informacoes_crianca['nome']}? ✨",
        f"Amiguinho de Jesus: Que maravilha, {informacoes_crianca['cidade']}! Um lugar onde a magia do Evangelho também pode florescer! O que você gostaria de aprender hoje, {informacoes_crianca['nome']}? ⭐",
        f"Amiguinho de Jesus: {informacoes_crianca['cidade']}! Que lugar especial! Estou aqui para compartilhar contigo as maravilhas do Evangelho. O que te interessa, {informacoes_crianca['termo_genero']}? 💖",
        f"Amiguinho de Jesus: {informacoes_crianca['cidade']}! Sinto a magia desse lugar daqui! Vamos descobrir juntos os tesouros do conhecimento, {informacoes_crianca['termo_genero']}? Qual a sua primeira pergunta hoje? ✨"
    ]
    mensagem_inicio_conversa_selecionada = random.choice(mensagens_inicio_conversa)
    print(mensagem_inicio_conversa_selecionada)
    historico_conversa.append({"role": "MODEL", "parts": [{"text": mensagem_inicio_conversa_selecionada}]}) # Adiciona ao histórico
    time.sleep(1.5)

    # Loop principal do chat
    while True:
        # # Define a cor e o prefixo do usuário com base no gênero a cada iteração do loop - REMOVIDO
        # if informacoes_crianca.get('genero') == 'masculino':
        #     cor_usuario = COR_AZUL
        #     prefixo_usuario = informacoes_crianca['nome']
        # elif informacoes_crianca.get('genero') == 'feminino':
        #     cor_usuario = COR_ROSA
        #     prefixo_usuario = informacoes_crianca['nome']
        # else:
        #     cor_usuario = COR_PADRAO
        #     prefixo_usuario = "Você"
            
        pergunta_crianca = input(f"{informacoes_crianca['nome']}: ") # Removido cor_usuario, prefixo_usuario, COR_PADRAO
        historico_conversa.append({"role": "USER", "parts": [{"text": pergunta_crianca}]}) # Adiciona a pergunta do usuário ao histórico

        if pergunta_crianca.lower() in ["adeus", "tchau", "até amanhã", "vou dormir", "está tarde", "mamãe chamando"]:
            despedidas = [
                "Amiguinho de Jesus: Que a magia do Evangelho esteja sempre com você! Até a próxima! 👋💖",
                "Amiguinho de Jesus: Foi maravilhoso conversar com você! Que a luz de Jesus te guie sempre! ✨",
                "Amiguinho de Jesus: Até breve, aprendiz! Que a paz do Evangelho te acompanhe! ⭐",
                f"Amiguinho de Jesus: Que a força do amor esteja com você, sempre! Até mais, {informacoes_crianca['nome']}! 💖",
                f"Amiguinho de Jesus: Volte sempre que precisar, {informacoes_crianca['termo_genero']}! A magia do Evangelho te espera! 👋✨"
            ]
            despedida_selecionada = random.choice(despedidas)
            print(despedida_selecionada)
            historico_conversa.append({"role": "MODEL", "parts": [{"text": despedida_selecionada}]}) # Adiciona a despedida ao histórico
            break

        # Mensagens de pensamento aleatórias com toque de Harry Potter
        mensagens_pensando = [
            "Lançando um feitiço de pensamento... 🤔✨",
            "Preparando uma poção de sabedoria... ✍️🧪",
            "Consultando as runas do Evangelho... 💭🔮",
            "Deixa eu ver aqui no Mapa do Maroto... 🧐🗺️",
            "Quase conjurando a resposta perfeita... 😃✨",
            "Concentrando minha magia... ✨",
            "Buscando a resposta nas estrelas do Evangelho... 🌟",
            "Acalmando meu coração para te responder com carinho... 💖",
            "Deixa eu perguntar para o meu amigo Jesus... 😇",
            "Abrindo o meu coração para responder a sua pergunta... ❤️"
        ]
        print(random.choice(mensagens_pensando))
        time.sleep(1.5)

        resposta_do_bot = gerar_resposta(pergunta_crianca, historico_conversa, informacoes_crianca, modelo_chat)
        # O histórico da conversa já foi atualizado com a pergunta do usuário antes do if/else de despedida
        print("Amiguinho de Jesus:", resposta_do_bot)
        historico_conversa.append({"role": "MODEL", "parts": [{"text": resposta_do_bot}]})
        time.sleep(1.5)

if __name__ == "__main__":
    main()
    