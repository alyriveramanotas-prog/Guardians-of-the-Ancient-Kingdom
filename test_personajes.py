"""Pruebas automatizadas (Pytest) de Guardians of the Ancient Kingdom.

Ejecutar:  pytest -v
"""

import pytest

from personajes import (
    Arquero,
    Combate,
    Guerrero,
    Mago,
    Personaje,
    PersonajeDerrotadoError,
)


# ----------------------------------------------------------------------
# Creación y validaciones
# ----------------------------------------------------------------------
@pytest.mark.parametrize("clase", [Guerrero, Mago, Arquero])
def test_creacion_valida_de_cada_tipo(clase):
    personaje = clase("Héroe", 100, 30, 20)
    assert isinstance(personaje, Personaje)
    assert (personaje.nombre, personaje.vida) == ("Héroe", 100)
    assert (personaje.ataque, personaje.defensa) == (30, 20)
    assert personaje.esta_vivo()


def test_personaje_es_abstracto():
    with pytest.raises(TypeError):
        Personaje("Genérico", 100, 10, 10)


def test_subclase_sin_atacar_no_se_puede_instanciar():
    class Incompleto(Personaje):
        pass

    with pytest.raises(TypeError):
        Incompleto("X", 100, 10, 10)


@pytest.mark.parametrize("vida", [101, 1000, -1])
def test_rechaza_vida_fuera_de_rango(vida):
    with pytest.raises(ValueError):
        Guerrero("Arthas", vida, 30, 20)


def test_rechaza_vida_decimal():
    with pytest.raises(TypeError):
        Guerrero("Arthas", 50.5, 30, 20)


@pytest.mark.parametrize("nombre", ["", "   "])
def test_rechaza_nombre_vacio(nombre):
    with pytest.raises(ValueError):
        Mago(nombre, 100, 30, 20)


def test_rechaza_nombre_que_no_es_texto():
    with pytest.raises(TypeError):
        Mago(123, 100, 30, 20)


@pytest.mark.parametrize("ataque", [0, -5])
def test_rechaza_ataque_no_positivo(ataque):
    with pytest.raises(ValueError):
        Arquero("A", 100, ataque, 10)


def test_rechaza_defensa_negativa():
    with pytest.raises(ValueError):
        Arquero("A", 100, 10, -1)


def test_acepta_vida_cero_y_defensa_cero():
    personaje = Guerrero("Caído", 0, 10, 0)
    assert not personaje.esta_vivo()
    assert personaje.defensa == 0


def test_los_setters_tambien_validan():
    personaje = Guerrero("Arthas", 100, 30, 20)
    with pytest.raises(ValueError):
        personaje.vida = 150
    with pytest.raises(ValueError):
        personaje.ataque = 0
    with pytest.raises(ValueError):
        personaje.defensa = -3
    with pytest.raises(ValueError):
        personaje.nombre = ""
    assert personaje.vida == 100  # el valor válido anterior se conserva


# ----------------------------------------------------------------------
# Cálculo del daño de cada clase
# ----------------------------------------------------------------------
def _objetivo(defensa):
    return Mago("Blanco", 100, 10, defensa)


@pytest.mark.parametrize(
    "ataque, defensa, esperado",
    [(30, 10, 26), (25, 0, 30), (7, 0, 8), (10, 50, 0), (30, 36, 0)],
)
def test_danio_del_guerrero(ataque, defensa, esperado):
    objetivo = _objetivo(defensa)
    danio = Guerrero("G", 100, ataque, 5).atacar(objetivo)
    assert danio == esperado
    assert objetivo.vida == 100 - esperado


@pytest.mark.parametrize("defensa", [0, 20, 90])
def test_el_mago_ignora_la_defensa(defensa):
    objetivo = _objetivo(defensa)
    danio = Mago("M", 80, 40, 10).atacar(objetivo)
    assert danio == 40
    assert objetivo.vida == 60


@pytest.mark.parametrize(
    "ataque, defensa, esperado",
    [(35, 15, 40), (36, 35, 2), (15, 15, 0), (10, 50, 0)],
)
def test_danio_del_arquero(ataque, defensa, esperado):
    objetivo = _objetivo(defensa)
    danio = Arquero("A", 90, ataque, 5).atacar(objetivo)
    assert danio == esperado
    assert objetivo.vida == 100 - esperado


# ----------------------------------------------------------------------
# La vida nunca es negativa / derrotados no atacan
# ----------------------------------------------------------------------
def test_recibir_danio_devuelve_el_danio_efectivo():
    personaje = Guerrero("Frágil", 20, 10, 0)
    assert personaje.recibir_danio(50) == 20
    assert personaje.vida == 0


def test_la_vida_nunca_es_negativa():
    personaje = Guerrero("Frágil", 20, 10, 0)
    personaje.recibir_danio(50)
    assert personaje.vida == 0
    assert personaje.recibir_danio(10) == 0
    assert personaje.vida == 0


def test_recibir_danio_rechaza_valores_invalidos():
    personaje = Guerrero("Arthas", 100, 30, 20)
    with pytest.raises(ValueError):
        personaje.recibir_danio(-1)
    with pytest.raises(TypeError):
        personaje.recibir_danio(2.5)
    assert personaje.vida == 100


def test_no_se_vuelve_a_descontar_la_defensa_al_recibir_danio():
    personaje = Guerrero("Arthas", 100, 30, 50)
    personaje.recibir_danio(10)
    assert personaje.vida == 90


def test_un_personaje_derrotado_no_puede_atacar():
    caido = Guerrero("Caído", 10, 10, 0)
    enemigo = Mago("Enemigo", 50, 20, 5)
    enemigo.atacar(caido)
    with pytest.raises(PersonajeDerrotadoError):
        caido.atacar(enemigo)
    assert enemigo.vida == 50


def test_no_se_puede_atacar_a_un_derrotado():
    caido = Guerrero("Caído", 0, 10, 0)
    enemigo = Mago("Enemigo", 50, 20, 5)
    with pytest.raises(PersonajeDerrotadoError):
        enemigo.atacar(caido)


def test_objetivo_invalido_o_el_mismo_personaje():
    arquero = Arquero("Legolas", 90, 35, 15)
    with pytest.raises(TypeError):
        arquero.atacar(None)
    with pytest.raises(ValueError):
        arquero.atacar(arquero)


# ----------------------------------------------------------------------
# Combate
# ----------------------------------------------------------------------
def test_combate_del_enunciado():
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    combate = Combate(arthas, gandalf)

    resultado = combate.iniciar(verbose=False)

    assert resultado == Combate.VICTORIA
    assert combate.ganador is gandalf
    assert (arthas.vida, gandalf.vida) == (0, 2)
    assert [f["danio"] for f in combate.historial] == [26, 40, 26, 40, 26, 20]
    assert [f["vidas"] for f in combate.historial] == [
        (100, 54), (60, 54), (60, 28), (20, 28), (20, 2), (0, 2),
    ]
    assert combate.rondas == 3


def test_el_ganador_puede_ser_el_primer_atacante():
    thor = Guerrero("Thor", 100, 50, 30)
    aprendiz = Mago("Aprendiz", 30, 10, 0)
    combate = Combate(thor, aprendiz)
    combate.iniciar(verbose=False)
    assert combate.ganador is thor
    assert not aprendiz.esta_vivo()


def test_empate_tecnico_cuando_nadie_causa_dano():
    a = Guerrero("Roca A", 100, 10, 50)
    b = Guerrero("Roca B", 100, 10, 50)
    combate = Combate(a, b)
    assert combate.iniciar(verbose=False) == Combate.EMPATE_TECNICO
    assert combate.ganador is None
    assert (a.vida, b.vida) == (100, 100)
    assert combate.rondas == 1


def test_empate_por_limite_de_50_rondas():
    a = Guerrero("Escudo A", 100, 17, 19)  # 17 * 1.2 = 20 -> 1 de daño
    b = Guerrero("Escudo B", 100, 17, 19)
    combate = Combate(a, b)
    assert combate.iniciar(verbose=False) == Combate.EMPATE_LIMITE
    assert combate.rondas == 50
    assert (a.vida, b.vida) == (50, 50)


def test_combate_rechaza_participantes_invalidos():
    arthas = Guerrero("Arthas", 100, 30, 20)
    with pytest.raises(TypeError):
        Combate(arthas, "no soy un personaje")
    with pytest.raises(ValueError):
        Combate(arthas, arthas)
    with pytest.raises(PersonajeDerrotadoError):
        Combate(arthas, Mago("Caído", 0, 10, 0))


def test_combate_no_puede_iniciarse_dos_veces():
    combate = Combate(Guerrero("A", 100, 50, 0), Mago("B", 10, 10, 0))
    combate.iniciar(verbose=False)
    with pytest.raises(RuntimeError):
        combate.iniciar(verbose=False)


def test_cambiar_turno_alterna_al_atacante():
    combate = Combate(Guerrero("A", 100, 30, 20), Mago("B", 80, 40, 10))
    combate.cambiar_turno()
    combate.iniciar(verbose=False)
    assert combate.historial[0]["atacante"] == "B"


def test_nuevo_guardian_funciona_sin_modificar_combate():
    class Paladin(Personaje):
        def atacar(self, objetivo):
            self._validar_ataque(objetivo)
            return objetivo.recibir_danio(5)

    lancelot = Paladin("Lancelot", 100, 10, 10)
    merlin = Mago("Merlín", 10, 1, 0)
    combate = Combate(lancelot, merlin)
    combate.iniciar(verbose=False)
    assert combate.ganador is lancelot
