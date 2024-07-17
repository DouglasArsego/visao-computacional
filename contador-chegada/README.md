                                            == Escolha Problema ==

Foi alterado Projeto, o projeto agora constiste em contar quantas pessoas passaram pela "linha de chegada"(linha vertical) usando como base o "rastreio de pessoas", em vez de contar quantos quadrados (pessoas) tem tela atualmente, ele deve contar quantos passaram pela linha vertical que sera colocada no centro da tela

                                                == Autor ==

Douglas Arsego

                                                == Implemtançao ==

O contador estava marcando uma pessoa varias vezes quando passava pela linha, entao foi implemtado uma funcao de tempo e distancia entre os quadros, o que garantiu que ela fosse contada apenas uma vez.

Ele ainda nao consegue marcar com 100% de precisao se uma pessoa passa muito proxima da outra, mas nesse caso é pelo video em si. Algum outro video que tenha essa "distancia" entre as pessoas vai funcionar 100%.

                                                == IMPORTANTE ==

Todo Projeto esta na pasta "contador-chegada".
Nao foi comitado junto o "frozen_inference_graph.pb" é preciso colocalo na pasta "contador-chegada".
