"""Guardians of the Ancient Kingdom: ejecución del programa y casos de prueba.

Uso:  python main.py
"""

from personajes import (
    Arquero,
    Combate,
    Guerrero,
    Mago,
    Personaje,
    PersonajeDerrotadoError,
)

resultados = []  # True/False de cada comprobación, para el resumen final


def titulo(texto):
    print()
    print("=" * 72)
    print(texto)
    print("=" * 72)


def comprobar(condicion, descripcion):
    resultados.append(bool(condicion))
    print(f"  [{'OK' if condicion else 'FALLO'}] {descripcion}")


def rechaza(accion, excepcion, descripcion):
    """Comprueba que accion() lance la excepción esperada."""
    try:
        accion()
    except Exception as error:  # noqa: BLE001 (se revisa el tipo abajo)
        comprobar(
            isinstance(error, excepcion),
            f"{descripcion} -> {type(error).__name__}: {error}",
        )
    else:
        comprobar(False, f"{descripcion} -> NO fue rechazado")


def imprimir_tabla(combate, p1, p2, vidas_iniciales):
    print(
        f"  {'Turno':<8}{'Atacante':<12}{'Daño':>6}"
        f"{'Vida ' + p1:>16}{'Vida ' + p2:>16}"
    )
    print(
        f"  {'Inicio':<8}{'-':<12}{'-':>6}"
        f"{vidas_iniciales[0]:>16}{vidas_iniciales[1]:>16}"
    )
    for fila in combate.historial:
        print(
            f"  {fila['turno']:<8}{fila['atacante']:<12}{fila['danio']:>6}"
            f"{fila['vidas'][0]:>16}{fila['vidas'][1]:>16}"
        )


# ----------------------------------------------------------------------
# Casos de prueba obligatorios
# ----------------------------------------------------------------------
def caso_1():
    titulo("Caso 1: creación correcta de los tres tipos de personajes")
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    legolas = Arquero("Legolas", 90, 35, 15)
    for personaje in (arthas, gandalf, legolas):
        print("  " + personaje.mostrar_estado())
        comprobar(
            isinstance(personaje, Personaje) and personaje.esta_vivo(),
            f"{personaje.nombre} es un Personaje válido y está vivo",
        )
    rechaza(
        lambda: Personaje("Genérico", 100, 10, 10),
        TypeError,
        "Instanciar la clase abstracta Personaje",
    )


def caso_2():
    titulo("Caso 2: rechazo de vida superior a 100 o negativa")
    for vida in (101, 1000, -1):
        rechaza(
            lambda v=vida: Guerrero("Arthas", v, 30, 20),
            ValueError,
            f"Vida {vida}",
        )
    rechaza(lambda: Mago("Merlín", 50.5, 10, 5), TypeError, "Vida decimal 50.5")


def caso_3():
    titulo("Caso 3: rechazo de nombres vacíos")
    rechaza(lambda: Guerrero("", 100, 30, 20), ValueError, "Nombre ''")
    rechaza(lambda: Mago("   ", 100, 30, 20), ValueError, "Nombre '   '")
    rechaza(lambda: Arquero(123, 100, 30, 20), TypeError, "Nombre numérico")


def caso_4():
    titulo("Caso 4: rechazo de ataques y defensas inválidos")
    rechaza(lambda: Guerrero("A", 100, 0, 20), ValueError, "Ataque 0")
    rechaza(lambda: Guerrero("A", 100, -5, 20), ValueError, "Ataque -5")
    rechaza(lambda: Guerrero("A", 100, 3.5, 20), TypeError, "Ataque 3.5")
    rechaza(lambda: Mago("M", 100, 30, -1), ValueError, "Defensa -1")
    rechaza(lambda: Mago("M", 100, 30, "10"), TypeError, "Defensa '10'")
    comprobar(
        Mago("M", 100, 30, 0).defensa == 0,
        "Defensa 0 sí es válida (no negativa)",
    )


def caso_5():
    titulo("Caso 5: habilidad del Guerrero (golpe poderoso)")
    guerrero = Guerrero("Arthas", 100, 30, 20)
    objetivo = Mago("Blanco", 100, 10, 10)
    danio = guerrero.atacar(objetivo)
    print(f"  Ataque 30 x 1.20 = 36; defensa 10 -> daño {danio}")
    comprobar(danio == 26, "Daño causado = 26")
    comprobar(objetivo.vida == 74, "Vida del objetivo = 74")
    objetivo_2 = Mago("Blanco 2", 100, 10, 0)
    danio_2 = Guerrero("G", 100, 7, 5).atacar(objetivo_2)
    comprobar(danio_2 == 8, "7 x 1.20 = 8.4 se redondea hacia abajo -> 8")


def caso_6():
    titulo("Caso 6: ataque del Mago ignora la defensa")
    mago = Mago("Gandalf", 80, 40, 10)
    objetivo = Guerrero("Blindado", 100, 10, 20)
    danio = mago.atacar(objetivo)
    print(f"  Ataque 40 contra defensa 20 -> daño {danio}")
    comprobar(danio == 40, "Daño causado = 40 (defensa ignorada)")
    comprobar(objetivo.vida == 60, "Vida del objetivo = 60")


def caso_7():
    titulo("Caso 7: disparo crítico del Arquero")
    arquero = Arquero("Legolas", 90, 35, 15)
    objetivo = Guerrero("Blanco", 100, 10, 15)
    danio = arquero.atacar(objetivo)
    print(f"  Ataque 35 contra defensa 15 -> base 20 x 2 = {danio}")
    comprobar(danio == 40, "Daño crítico = 40")
    comprobar(objetivo.vida == 60, "Vida del objetivo = 60")
    muralla = Guerrero("Muralla", 100, 10, 50)
    danio_cero = arquero.atacar(muralla)
    comprobar(danio_cero == 0, "Ataque 35 no supera defensa 50 -> daño 0")
    comprobar(muralla.vida == 100, "La vida del objetivo no cambia")


def caso_8():
    titulo("Caso 8: imposibilidad de tener vida negativa")
    personaje = Guerrero("Frágil", 20, 10, 0)
    recibido = personaje.recibir_danio(50)
    print(f"  Vida 20 recibe 50 de daño -> efectivo {recibido}")
    comprobar(recibido == 20, "El daño efectivo recibido es 20")
    comprobar(personaje.vida == 0, "La vida queda en 0, no en -30")
    comprobar(not personaje.esta_vivo(), "El personaje está derrotado")
    rechaza(lambda: setattr(personaje, "vida", -5), ValueError, "Asignar vida -5")
    rechaza(lambda: personaje.recibir_danio(-10), ValueError, "Daño negativo")


def caso_9():
    titulo("Caso 9: imposibilidad de atacar estando derrotado")
    caido = Guerrero("Caído", 10, 10, 0)
    enemigo = Mago("Enemigo", 50, 20, 5)
    enemigo.atacar(caido)
    comprobar(not caido.esta_vivo(), "Caído quedó derrotado")
    rechaza(
        lambda: caido.atacar(enemigo),
        PersonajeDerrotadoError,
        "Un derrotado intenta atacar",
    )
    rechaza(
        lambda: enemigo.atacar(caido),
        PersonajeDerrotadoError,
        "Se ataca a un derrotado",
    )
    rechaza(lambda: enemigo.atacar(None), TypeError, "Objetivo inválido (None)")
    comprobar(enemigo.vida == 50, "El enemigo no sufrió daño")


def caso_10_y_11():
    titulo("Casos 10 y 11: combate completo e identificación del ganador")
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    combate = Combate(arthas, gandalf)
    combate.iniciar()  # muestra el estado después de cada ataque

    print()
    imprimir_tabla(combate, "Arthas", "Gandalf", (100, 80))
    print()
    danios = [fila["danio"] for fila in combate.historial]
    comprobar(danios == [26, 40, 26, 40, 26, 20], f"Daños por turno {danios}")
    comprobar(arthas.vida == 0 and gandalf.vida == 2, "Vidas finales 0 y 2")
    comprobar(combate.resultado == Combate.VICTORIA, "Resultado: victoria")
    comprobar(combate.ganador is gandalf, "Ganador identificado: Gandalf")

    thor = Guerrero("Thor", 100, 50, 30)
    aprendiz = Mago("Aprendiz", 30, 10, 0)
    combate_2 = Combate(thor, aprendiz)
    combate_2.iniciar(verbose=False)
    print("  " + combate_2.mostrar_resultado())
    comprobar(combate_2.ganador is thor, "Segundo combate: gana Thor")


def caso_12():
    titulo("Caso 12: combate sin daño -> empate técnico")
    roca_a = Guerrero("Roca A", 100, 10, 50)
    roca_b = Guerrero("Roca B", 100, 10, 50)
    combate = Combate(roca_a, roca_b)
    combate.iniciar(verbose=False)
    print("  " + combate.mostrar_resultado())
    comprobar(combate.resultado == Combate.EMPATE_TECNICO, "Empate técnico")
    comprobar(combate.ganador is None, "No hay ganador")
    comprobar(roca_a.vida == 100 and roca_b.vida == 100, "Nadie perdió vida")
    comprobar(combate.rondas == 1, "Termina en la primera ronda")


def caso_extra():
    titulo("Extra: límite de 50 rondas sin ganador")
    a = Guerrero("Escudo A", 100, 17, 19)
    b = Guerrero("Escudo B", 100, 17, 19)
    combate = Combate(a, b)
    combate.iniciar(verbose=False)
    print("  " + combate.mostrar_resultado())
    print(f"  Vidas finales: {a.vida} y {b.vida}")
    comprobar(combate.resultado == Combate.EMPATE_LIMITE, "Empate por límite")
    comprobar(combate.rondas == 50, "Se completaron 50 rondas")
    comprobar(a.esta_vivo() and b.esta_vivo(), "Ambos siguen vivos")


def main():
    caso_1()
    caso_2()
    caso_3()
    caso_4()
    caso_5()
    caso_6()
    caso_7()
    caso_8()
    caso_9()
    caso_10_y_11()
    caso_12()
    caso_extra()

    titulo("Resumen")
    superadas = sum(resultados)
    print(f"  {superadas} de {len(resultados)} comprobaciones superadas.")
    raise SystemExit(0 if superadas == len(resultados) else 1)


if __name__ == "__main__":
    main()
