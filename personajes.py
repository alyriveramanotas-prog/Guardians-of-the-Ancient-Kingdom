"""Guardians of the Ancient Kingdom: clases del sistema de combate por turnos.

Este módulo solo DEFINE las clases del sistema. No imprime ni ejecuta pruebas
al importarse: la creación de objetos y las pruebas viven en main.py.
"""

from abc import ABC, abstractmethod


class PersonajeDerrotadoError(Exception):
    """Se lanza cuando un personaje derrotado intenta atacar o es atacado."""


def _es_entero(valor):
    """Devuelve True si valor es un entero (bool se excluye a propósito)."""
    return isinstance(valor, int) and not isinstance(valor, bool)


class Personaje(ABC):
    """Clase abstracta con las características y comportamientos comunes."""

    VIDA_MAXIMA = 100

    def __init__(self, nombre, vida, ataque, defensa):
        # Se asigna a través de los setters para que toda la validación
        # viva en un único lugar.
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque
        self.defensa = defensa

    # ------------------------------------------------------------------
    # Atributos encapsulados (getters y setters con validación)
    # ------------------------------------------------------------------
    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str):
            raise TypeError("El nombre debe ser un texto.")
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self.__nombre = valor.strip()

    @property
    def vida(self):
        return self.__vida

    @vida.setter
    def vida(self, valor):
        if not _es_entero(valor):
            raise TypeError("La vida debe ser un número entero.")
        if not 0 <= valor <= self.VIDA_MAXIMA:
            raise ValueError(
                f"La vida debe estar entre 0 y {self.VIDA_MAXIMA}."
            )
        self.__vida = valor

    @property
    def ataque(self):
        return self.__ataque

    @ataque.setter
    def ataque(self, valor):
        if not _es_entero(valor):
            raise TypeError("El ataque debe ser un número entero.")
        if valor <= 0:
            raise ValueError("El ataque debe ser un entero positivo.")
        self.__ataque = valor

    @property
    def defensa(self):
        return self.__defensa

    @defensa.setter
    def defensa(self, valor):
        if not _es_entero(valor):
            raise TypeError("La defensa debe ser un número entero.")
        if valor < 0:
            raise ValueError("La defensa no puede ser negativa.")
        self.__defensa = valor

    # ------------------------------------------------------------------
    # Comportamientos comunes
    # ------------------------------------------------------------------
    def recibir_danio(self, cantidad):
        """Resta vida y devuelve el daño efectivamente recibido.

        El daño llega ya calculado por el atacante: aquí NO se vuelve a
        descontar la defensa.
        """
        if not _es_entero(cantidad):
            raise TypeError("El daño debe ser un número entero.")
        if cantidad < 0:
            raise ValueError("El daño no puede ser negativo.")
        danio_recibido = min(cantidad, self.vida)
        self.vida = self.vida - danio_recibido
        return danio_recibido

    def esta_vivo(self):
        return self.vida > 0

    def mostrar_estado(self):
        """Devuelve un texto con el estado actual del personaje."""
        estado = "vivo" if self.esta_vivo() else "derrotado"
        return (
            f"{self.nombre} [{type(self).__name__}] "
            f"Vida: {self.vida}/{self.VIDA_MAXIMA} | "
            f"Ataque: {self.ataque} | Defensa: {self.defensa} | {estado}"
        )

    def _validar_ataque(self, objetivo):
        """Validaciones comunes que usan las tres clases hijas al atacar."""
        if not isinstance(objetivo, Personaje):
            raise TypeError("El objetivo debe ser un Personaje.")
        if objetivo is self:
            raise ValueError("Un personaje no puede atacarse a sí mismo.")
        if not self.esta_vivo():
            raise PersonajeDerrotadoError(
                f"{self.nombre} está derrotado y no puede atacar."
            )
        if not objetivo.esta_vivo():
            raise PersonajeDerrotadoError(
                f"{objetivo.nombre} ya está derrotado y no puede ser atacado."
            )

    @abstractmethod
    def atacar(self, objetivo):
        """Ataca al objetivo y devuelve el daño efectivamente causado."""


class Guerrero(Personaje):
    """Golpe poderoso: ataque +20 % antes de descontar la defensa."""

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        # Aritmética entera: ataque * 1.20 redondeado hacia abajo,
        # sin errores de punto flotante.
        ataque_potenciado = self.ataque * 120 // 100
        danio = max(0, ataque_potenciado - objetivo.defensa)
        return objetivo.recibir_danio(danio)


class Mago(Personaje):
    """Hechizo penetrante: ignora por completo la defensa del objetivo."""

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        return objetivo.recibir_danio(self.ataque)


class Arquero(Personaje):
    """Disparo crítico: duplica el daño si el ataque supera la defensa."""

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        if self.ataque > objetivo.defensa:
            danio = (self.ataque - objetivo.defensa) * 2
        else:
            danio = 0
        return objetivo.recibir_danio(danio)


class Combate:
    """Administra un enfrentamiento por turnos entre dos personajes.

    Agregación: los personajes se crean fuera y se entregan al combate.
    Polimorfismo: solo llama a atacar(); nunca pregunta el tipo concreto.
    """

    MAX_RONDAS = 50

    VICTORIA = "victoria"
    EMPATE_TECNICO = "empate técnico"
    EMPATE_LIMITE = "empate por límite de rondas"

    def __init__(self, personaje1, personaje2):
        for personaje in (personaje1, personaje2):
            if not isinstance(personaje, Personaje):
                raise TypeError("Los participantes deben ser Personajes.")
            if not personaje.esta_vivo():
                raise PersonajeDerrotadoError(
                    f"{personaje.nombre} está derrotado y no puede combatir."
                )
        if personaje1 is personaje2:
            raise ValueError("Un personaje no puede combatir contra sí mismo.")

        self.__participantes = (personaje1, personaje2)
        self.__turno_actual = 0  # índice del personaje que debe atacar
        self.__turnos = 0
        self.__rondas = 0
        self.__ganador = None
        self.__resultado = None  # None mientras el combate no haya terminado
        self.__historial = []

    # ------------------------------------------------------------------
    # Consulta
    # ------------------------------------------------------------------
    @property
    def ganador(self):
        return self.__ganador

    @property
    def resultado(self):
        return self.__resultado

    @property
    def rondas(self):
        return self.__rondas

    @property
    def historial(self):
        """Copia del registro de ataques (uno por turno)."""
        return [dict(entrada) for entrada in self.__historial]

    # ------------------------------------------------------------------
    # Lógica del combate
    # ------------------------------------------------------------------
    def cambiar_turno(self):
        """Alterna el personaje que debe atacar."""
        self.__turno_actual = 1 - self.__turno_actual

    def verificar_ganador(self):
        """Devuelve el personaje vencedor o None si ambos siguen en pie."""
        primero, segundo = self.__participantes
        if not primero.esta_vivo():
            return segundo
        if not segundo.esta_vivo():
            return primero
        return None

    def iniciar(self, verbose=True):
        """Ejecuta el combate completo y devuelve su resultado."""
        if self.__resultado is not None:
            raise RuntimeError("El combate ya terminó.")

        if verbose:
            print("=== Inicio del combate ===")
            self.__imprimir_estados()

        while self.__resultado is None:
            self.__rondas += 1
            danio_ronda = 0

            for _ in range(2):  # cada personaje ataca una vez por ronda
                atacante = self.__participantes[self.__turno_actual]
                objetivo = self.__participantes[1 - self.__turno_actual]

                danio = atacante.atacar(objetivo)  # polimorfismo
                self.__turnos += 1
                danio_ronda += danio
                self.__registrar(atacante, danio)

                if verbose:
                    print(
                        f"Turno {self.__turnos}: {atacante.nombre} ataca a "
                        f"{objetivo.nombre} y causa {danio} de daño."
                    )
                    self.__imprimir_estados()

                ganador = self.verificar_ganador()
                if ganador is not None:
                    self.__ganador = ganador
                    self.__resultado = self.VICTORIA
                    break
                self.cambiar_turno()

            if self.__resultado is None:
                if danio_ronda == 0:
                    self.__resultado = self.EMPATE_TECNICO
                elif self.__rondas >= self.MAX_RONDAS:
                    self.__resultado = self.EMPATE_LIMITE

        if verbose:
            print(self.mostrar_resultado())
        return self.__resultado

    def mostrar_resultado(self):
        """Devuelve un texto con el resultado final del combate."""
        if self.__resultado is None:
            return "El combate aún no ha terminado."
        if self.__resultado == self.VICTORIA:
            g = self.__ganador
            return (
                f"Ganador: {g.nombre} [{type(g).__name__}] con {g.vida} de "
                f"vida tras {self.__rondas} rondas ({self.__turnos} turnos)."
            )
        if self.__resultado == self.EMPATE_TECNICO:
            return (
                f"Empate técnico: nadie logró causar daño en la ronda "
                f"{self.__rondas}."
            )
        return (
            f"Empate: se completaron {self.MAX_RONDAS} rondas sin ganador."
        )

    # ------------------------------------------------------------------
    # Apoyo interno
    # ------------------------------------------------------------------
    def __registrar(self, atacante, danio):
        primero, segundo = self.__participantes
        self.__historial.append(
            {
                "turno": self.__turnos,
                "atacante": atacante.nombre,
                "danio": danio,
                "vidas": (primero.vida, segundo.vida),
            }
        )

    def __imprimir_estados(self):
        for personaje in self.__participantes:
            print("   " + personaje.mostrar_estado())
