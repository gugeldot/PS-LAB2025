"""
Mediator Pattern - Centralizar comunicación entre componentes

Reduce el acoplamiento entre objetos al evitar que se comuniquen directamente.
El mediador gestiona todas las interacciones.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class Mediator(ABC):
    """Interfaz base para mediadores"""
    
    @abstractmethod
    def notify(self, sender: object, event: str, data: Dict[str, Any] = None) -> None:
        """
        Recibe notificación de un componente y coordina respuestas
        
        Args:
            sender: Objeto que envía la notificación
            event: Tipo de evento
            data: Datos adicionales del evento
        """
        pass


class GameMediator(Mediator):
    """
    Mediador central del juego que coordina interacciones entre:
    - UI (HUD, menús)
    - Estados del juego
    - Estructuras
    - Sistema de puntos
    """
    
    def __init__(self, gameManager):
        self.gameManager = gameManager
        self.hud = None
        self.mouse_control = None
        self._components: Dict[str, object] = {}
    
    def register_component(self, name: str, component: object) -> None:
        """Registra un componente para que pueda comunicarse"""
        self._components[name] = component
    
    def notify(self, sender: object, event: str, data: Dict[str, Any] = None) -> None:
        """Procesa eventos y coordina respuestas entre componentes"""
        if data is None:
            data = {}
        
        # UI Events
        if event == 'button_clicked':
            self._handle_button_click(data)
        
        # Structure Events
        elif event == 'structure_placed':
            self._handle_structure_placed(data)
        
        elif event == 'structure_destroyed':
            self._handle_structure_destroyed(data)
        
        # Game State Events
        elif event == 'state_changed':
            self._handle_state_change(data)
        
        # Points Events
        elif event == 'points_earned':
            self._handle_points_earned(data)
        
        elif event == 'points_spent':
            self._handle_points_spent(data)
        
        # Upgrade Events
        elif event == 'upgrade_purchased':
            self._handle_upgrade_purchased(data)
        
        # Connection Events
        elif event == 'conveyor_connected':
            self._handle_conveyor_connected(data)
    
    def _handle_button_click(self, data: Dict[str, Any]) -> None:
        """Maneja clics en botones de UI"""
        button_type = data.get('button')
        
        if button_type == 'build_mode':
            # Cambiar a modo construcción
            if hasattr(self.gameManager, 'buildState'):
                self.gameManager.setState(self.gameManager.buildState)
                if self.hud:
                    self.hud.show_message("Modo construcción", 1000)
        
        elif button_type == 'destroy_mode':
            # Cambiar a modo destrucción
            if hasattr(self.gameManager, 'destroyState'):
                self.gameManager.setState(self.gameManager.destroyState)
                if self.hud:
                    self.hud.show_message("Modo destrucción", 1000)
        
        elif button_type == 'normal_mode':
            # Volver a modo normal
            if hasattr(self.gameManager, 'normalState'):
                self.gameManager.setState(self.gameManager.normalState)
        
        elif button_type == 'save_game':
            # Guardar juego
            self._save_game()
        
        elif button_type == 'load_game':
            # Cargar juego
            self._load_game()
    
    def _handle_structure_placed(self, data: Dict[str, Any]) -> None:
        """Maneja colocación de estructuras"""
        structure = data.get('structure')
        cost = data.get('cost', 0)
        
        # Deducir puntos
        if hasattr(self.gameManager, 'points'):
            self.gameManager.points -= cost
        
        # Reconectar estructuras si es necesario
        if hasattr(self.gameManager, '_reconnect_structures'):
            self.gameManager._reconnect_structures()
        
        # Notificar a HUD
        if self.hud:
            self.hud.show_message(f"Estructura construida (-{cost} pts)", 1500)
    
    def _handle_structure_destroyed(self, data: Dict[str, Any]) -> None:
        """Maneja destrucción de estructuras"""
        structure = data.get('structure')
        refund = data.get('refund', 0)
        
        # Devolver puntos
        if hasattr(self.gameManager, 'points'):
            self.gameManager.points += refund
        
        # Reconectar estructuras
        if hasattr(self.gameManager, '_reconnect_structures'):
            self.gameManager._reconnect_structures()
        
        # Notificar a HUD
        if self.hud:
            self.hud.show_message(f"Estructura destruida (+{refund} pts)", 1500)
    
    def _handle_state_change(self, data: Dict[str, Any]) -> None:
        """Maneja cambios de estado del juego"""
        old_state = data.get('old_state')
        new_state = data.get('new_state')
        
        # Actualizar UI según estado
        if self.hud:
            state_name = new_state.__class__.__name__
            # self.hud.update_state_indicator(state_name)
    
    def _handle_points_earned(self, data: Dict[str, Any]) -> None:
        """Maneja ganancia de puntos"""
        amount = data.get('amount', 0)
        source = data.get('source', 'unknown')
        
        # Mostrar notificación si es significativo
        if self.hud and amount >= 5:
            self.hud.show_message(f"+{amount} puntos!", 2000)
    
    def _handle_points_spent(self, data: Dict[str, Any]) -> None:
        """Maneja gasto de puntos"""
        amount = data.get('amount', 0)
        reason = data.get('reason', 'unknown')
        
        # Verificar si quedan puntos suficientes
        if hasattr(self.gameManager, 'points'):
            if self.gameManager.points < 0:
                print(f"⚠️ Warning: Negative points! Current: {self.gameManager.points}")
    
    def _handle_upgrade_purchased(self, data: Dict[str, Any]) -> None:
        """Maneja compra de mejoras"""
        upgrade_type = data.get('type', 'unknown')
        cost = data.get('cost', 0)
        
        # Notificar UI
        if self.hud:
            self.hud.show_message(f"Mejora comprada: {upgrade_type}", 2000)
    
    def _handle_conveyor_connected(self, data: Dict[str, Any]) -> None:
        """Maneja conexión de cintas"""
        start = data.get('start')
        end = data.get('end')
        
        # Reconectar todas las estructuras
        if hasattr(self.gameManager, '_reconnect_structures'):
            self.gameManager._reconnect_structures()
    
    def _save_game(self) -> None:
        """Guarda el estado del juego"""
        try:
            # Usar sistema de memento si está disponible
            if hasattr(self.gameManager, 'originator'):
                memento = self.gameManager.originator.create_memento("manual_save")
                if hasattr(self.gameManager, 'caretaker'):
                    self.gameManager.caretaker.save_snapshot("manual_save", memento)
                    if self.hud:
                        self.hud.show_message("Juego guardado", 2000)
        except Exception as e:
            print(f"Error saving game: {e}")
            if self.hud:
                self.hud.show_message("Error al guardar", 2000)
    
    def _load_game(self) -> None:
        """Carga el estado del juego"""
        try:
            # Usar sistema de memento si está disponible
            if hasattr(self.gameManager, 'caretaker'):
                memento = self.gameManager.caretaker.load_snapshot("manual_save")
                if memento and hasattr(self.gameManager, 'originator'):
                    self.gameManager.originator.restore_memento(memento)
                    if self.hud:
                        self.hud.show_message("Juego cargado", 2000)
        except Exception as e:
            print(f"Error loading game: {e}")
            if self.hud:
                self.hud.show_message("Error al cargar", 2000)


class StructureMediator(Mediator):
    """
    Mediador específico para comunicación entre estructuras
    Gestiona flujo de items entre estructuras conectadas
    """
    
    def __init__(self):
        self._structures: Dict[int, object] = {}
    
    def register_structure(self, structure_id: int, structure: object) -> None:
        """Registra una estructura"""
        self._structures[structure_id] = structure
    
    def unregister_structure(self, structure_id: int) -> None:
        """Desregistra una estructura"""
        if structure_id in self._structures:
            del self._structures[structure_id]
    
    def notify(self, sender: object, event: str, data: Dict[str, Any] = None) -> None:
        """Procesa eventos entre estructuras"""
        if data is None:
            data = {}
        
        if event == 'item_produced':
            self._route_item(sender, data)
        
        elif event == 'item_consumed':
            self._handle_consumption(sender, data)
        
        elif event == 'structure_upgraded':
            self._notify_connected_structures(sender, event, data)
    
    def _route_item(self, producer: object, data: Dict[str, Any]) -> None:
        """Enruta un item desde el productor a través de cintas"""
        item = data.get('item')
        
        # Verificar si hay cinta de salida
        if hasattr(producer, 'outputConveyor') and producer.outputConveyor:
            try:
                producer.outputConveyor.queue.append(item)
            except:
                pass
    
    def _handle_consumption(self, consumer: object, data: Dict[str, Any]) -> None:
        """Maneja consumo de items"""
        item = data.get('item')
        points = data.get('points', 0)
        
        # Notificar al sistema de puntos si está disponible
        if hasattr(consumer, 'gameManager'):
            if hasattr(consumer.gameManager, 'mediator'):
                consumer.gameManager.mediator.notify(
                    consumer, 
                    'points_earned', 
                    {'amount': points, 'source': 'well'}
                )
    
    def _notify_connected_structures(self, source: object, event: str, data: Dict[str, Any]) -> None:
        """Notifica a estructuras conectadas sobre cambios"""
        # Notificar a estructuras conectadas por cintas
        if hasattr(source, 'outputConveyor') and source.outputConveyor:
            # Propagar evento a estructuras conectadas
            pass
