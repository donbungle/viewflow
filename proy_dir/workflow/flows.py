from viewflow import flow
from viewflow import frontend
from viewflow.base import this, Flow
from viewflow.flow.views import CreateProcessView, UpdateProcessView

from .models import OperacionProcess


@frontend.register
class OperacionFlow(Flow):
    process_class = OperacionProcess

    inicio = (
        flow.Start(
            CreateProcessView,
            fields=["texto"]
        ).Next(this.aprobar_middle)
    )

    aprobar_middle = (
        flow.View(
            UpdateProcessView,
            fields=["aprobado_middle"]
        ).Permission('workflow.can_start_operation')
        .Next(this.check_aprobacion_middle)
    )

    check_aprobacion_middle = (
        flow.If(lambda activation: activation.process.aprobado_middle)
        .Then(this.aprobar_back)
        .Else(this.aprobar_middle)
    )

    aprobar_back = (
        flow.View(
            UpdateProcessView,
            fields=["aprobado_back"]
        ).Next(this.check_aprobacion_back)
    )

    check_aprobacion_back = (
        flow.If(lambda activation: activation.process.aprobado_back)
        .Then(this.aprobar_benito)
        .Else(this.aprobar_middle)
    )

    aprobar_benito = (
        flow.View(
            UpdateProcessView,
            fields=[
                "aprobado_benito",
                "aprobado_back",
                "aprobado_middle",
                "numero",
                "texto",
            ]
        ).Permission('workflow.can_see_hidden_field')
        .Next(this.check_aprobacion_benito)
    )

    check_aprobacion_benito = (
        flow.If(lambda activation: activation.process.aprobado_benito)
        .Then(this.notificacion)
        .Else(this.aprobar_back)
    )

    notificacion = (
        flow.Handler(
            this.enviar_notificacion
        ).Next(this.fin)
    )

    fin = flow.End()

    def enviar_notificacion(self, activation):
        print(activation.process)
        print('-'*50)
        print(f"{activation.process.texto}: {self.aprobado_por_benito(activation.process.aprobado_benito)}")

    def aprobado_por_benito(self, aprobado_benito):
        if aprobado_benito:
            mensaje = 'Aprobado'
        else:
            mensaje = 'Rechazado'
        return f'{mensaje} por Benito'
