import cv2
import numpy as np

# Caminhos dos arquivos
ARQUIVO_VIDEO = 'contador-chegada/running.mp4'
ARQUIVO_MODELO = 'contador-chegada/frozen_inference_graph.pb'
ARQUIVO_CFG = 'contador-chegada/ssd_mobilenet_v2_coco.pbtxt'

def carregar_modelo(ARQUIVO_MODELO, ARQUIVO_CFG):
    try:
        modelo = cv2.dnn.readNetFromTensorflow(ARQUIVO_MODELO, ARQUIVO_CFG)
    except cv2.error as erro:
        print(f"Erro ao carregar o modelo: {erro}")
        exit()
    return modelo

def aplicar_supressao_nao_maxima(caixas, confiancas, limiar_conf, limiar_supr):
    indices = cv2.dnn.NMSBoxes(caixas, confiancas, limiar_conf, limiar_supr)
    return [caixas[i] for i in indices.flatten()] if len(indices) > 0 else []

# Carregamento e Supresão se Mantiveram

def main():
    captura = cv2.VideoCapture(ARQUIVO_VIDEO)
    detector_pessoas = carregar_modelo(ARQUIVO_MODELO, ARQUIVO_CFG)
    pausado = False

    # Linha virtual vertical pra contar as pessoas
    altura_video = int(captura.get(cv2.CAP_PROP_FRAME_HEIGHT))
    largura_video = int(captura.get(cv2.CAP_PROP_FRAME_WIDTH))
    linha_x = largura_video // 2 
    pessoas_contagem = 0

    rastreamento = {} # Usa dicionario pra gerenciar rastremanto
    tempo_desaparecimento = 50 # Usado no rastreio

# Se manteve o laço e a criação da blob
    while True:
        if not pausado:
            ret, frame = captura.read()
            if not ret:
                break
            
            blob = cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True, crop=False)
            detector_pessoas.setInput(blob)
            deteccoes = detector_pessoas.forward()

            caixas = []
            confiancas = []

            for i in range(deteccoes.shape[2]):
                confianca = deteccoes[0, 0, i, 2]
                if confianca > 0.5:
                    (altura, largura) = frame.shape[:2]
                    caixa = deteccoes[0, 0, i, 3:7] * np.array([largura, altura, largura, altura])
                    (inicioX, inicioY, fimX, fimY) = caixa.astype("int")
                    caixas.append([inicioX, inicioY, fimX - inicioX, fimY - inicioY])
                    confiancas.append(float(confianca))

            caixas_finais = aplicar_supressao_nao_maxima(caixas, confiancas, limiar_conf=0.5, limiar_supr=0.4)
# Ate aqui


#Logica para detectar se a pessoa passou na linha
            
            novas_caixas = {} #Calcula o centro da caixa e armazena no dicionário
            for idx, (inicioX, inicioY, largura, altura) in enumerate(caixas_finais):
                centroX = inicioX + largura // 2
                novas_caixas[idx] = (inicioX, inicioY, largura, altura, centroX)

            # Atualização do rastreamento de objetos
            ids_para_remover = []
            for id, (x, y, l, h, centroX_prev, frames_desaparecidos) in rastreamento.items():
                rastreamento[id] = (x, y, l, h, centroX_prev, frames_desaparecidos + 1)
                if frames_desaparecidos > tempo_desaparecimento:
                    ids_para_remover.append(id)

            for id in ids_para_remover: # Remove os objetos rastreados que estiveram ausentes por muito tempo
                del rastreamento[id]

            # Cada nova detecção calcula o centro com de outros objetos, se for distante o bastante 
            # cria novo objeto que ao passar da linha conta como uma pessoa
            for idx, (inicioX, inicioY, largura, altura, centroX) in novas_caixas.items():
                melhor_id = None
                menor_distancia = float("inf")
                for id, (x, y, l, h, centroX_prev, frames_desaparecidos) in rastreamento.items():
                    distancia = abs(centroX - centroX_prev)
                    if distancia < menor_distancia and frames_desaparecidos <= tempo_desaparecimento:
                        menor_distancia = distancia
                        melhor_id = id

                if melhor_id is None or menor_distancia > largura // 2:
                    novo_id = max(rastreamento.keys(), default=0) + 1
                    rastreamento[novo_id] = (inicioX, inicioY, largura, altura, centroX, 0)
                else:
                    x, y, l, h, centroX_prev, _ = rastreamento[melhor_id]
                    if centroX_prev < linha_x <= centroX:
                        pessoas_contagem += 1
                    rastreamento[melhor_id] = (inicioX, inicioY, largura, altura, centroX, 0)

            # Parecido com original mas usa rastreamento e nao as caixas finais pra contar
            for (inicioX, inicioY, largura, altura, _, _) in rastreamento.values():
                cv2.rectangle(frame, (inicioX, inicioY), (inicioX + largura, inicioY + altura), (0, 255, 0), 2)
            cv2.putText(frame, f"Pessoas contadas: {pessoas_contagem}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Desenho da linha
            cv2.line(frame, (linha_x, 0), (linha_x, altura_video), (255, 0, 0), 2)

        # Desenho Frame
        cv2.imshow("Rastreio de Pessoas", frame)
        
        tecla = cv2.waitKey(30) & 0xFF
        if tecla == ord('q'):
            break
        elif tecla == ord('p'):
            pausado = not pausado


    captura.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()