from modelo.motor_simulacion import MotorSimulacion
from modelo.colas.mmc import mmc_metricas
from modelo.persistencia.repositorio_resultados import RepositorioResultados


class ControladorSimulacion:
    def __init__(self):
        self.resultado = None
        self.validacion = None
        self.trazas = []
        self.repo_resultados = RepositorioResultados()

    def ejecutar(self, config: dict, escenario_id: int = None) -> dict:
        motor = MotorSimulacion(
            num_operadores=config["num_operadores"],
            tasa_llegada=config["tasa_llegada"],
            tasa_servicio=config["tasa_servicio"],
            tiempo_simulacion=config["tiempo_simulacion"],
        )
        self.resultado = motor.ejecutar()
        self.trazas = motor.trazas
        self.validacion = mmc_metricas(
            config["tasa_llegada"], config["tasa_servicio"],
            config["num_operadores"]
        )

        if escenario_id is None:
            escenario_id = config.get("escenario_id")
        if escenario_id:
            self.repo_resultados.guardar(escenario_id, self.resultado)

        return self.resultado

    def comparar_con_analitico(self):
        """Compara las métricas simuladas con el modelo M/M/c."""
        if not self.resultado or not self.validacion:
            return None
        if not self.validacion.get("estable"):
            return {"estado": "inestable", "rho": self.validacion.get("rho")}
        return {
            "Wq_simulado": self.resultado["espera_promedio"],
            "Wq_analitico": self.validacion["Wq"],
            "utilizacion_simulada": self.resultado["utilizacion_operadores"],
            "utilizacion_analitica": self.validacion["rho"],
        }