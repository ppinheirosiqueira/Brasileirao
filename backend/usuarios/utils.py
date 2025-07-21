import random
import colorsys
def gerar_cor_clara():
    # Gerar um valor de cor aleatório em tons claros
    # Você pode ajustar os valores de mínimo e máximo para controlar a gama de cores claras geradas
    h = random.uniform(0.0, 1.0)  # Matiz
    s = random.uniform(0.3, 0.7)  # Saturação
    v = random.uniform(0.7, 1.0)  # Valor

    # Converter a cor de HSV para RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)

    # Converter os valores de RGB para hexadecimal
    cor_hex = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

    return cor_hex