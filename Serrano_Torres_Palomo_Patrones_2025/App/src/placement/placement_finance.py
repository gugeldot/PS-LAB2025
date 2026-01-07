def compute_cost(controller):
    """Return integer cost for the current factory, respecting gameManager.build_costs mapping
    and falling back to factory.getCost() like the original method.
    """
    try:
        costs_map = getattr(controller.gameManager, 'build_costs', None) or {}
        cname = controller.factory.__class__.__name__.lower() if controller.factory is not None else ''
        if costs_map:
            if 'sum' in cname:
                return int(costs_map.get('sum', controller.factory.getCost()))
            elif 'mul' in cname or 'multiply' in cname:
                return int(costs_map.get('mul', controller.factory.getCost()))
            elif 'div' in cname:
                return int(costs_map.get('div', controller.factory.getCost()))
            elif 'splitter' in cname:
                return int(costs_map.get('splitter', controller.factory.getCost()))
            elif 'merger' in cname:
                return int(costs_map.get('merger', controller.factory.getCost()))
            elif 'conveyor' in cname or 'convey' in cname:
                return int(costs_map.get('conveyor', controller.factory.getCost()))
        return int(controller.factory.getCost())
    except Exception:
        try:
            return int(controller.factory.getCost())
        except Exception:
            return 0


def compute_refund(controller, structure):
    """Return integer refund for a structure, mirroring the original refund computation.
    """
    try:
        costs_map = getattr(controller.gameManager, 'build_costs', None) or {}
        sname = structure.__class__.__name__.lower()
        if costs_map:
            if 'sum' in sname:
                return int(costs_map.get('sum', structure.getCost()))
            elif 'mul' in sname or 'multiply' in sname:
                return int(costs_map.get('mul', structure.getCost()))
            elif 'div' in sname:
                return int(costs_map.get('div', structure.getCost()))
            elif 'splitter' in sname:
                return int(costs_map.get('splitter', structure.getCost()))
            elif 'merger' in sname:
                return int(costs_map.get('merger', structure.getCost()))
            elif 'conveyor' in sname or 'convey' in sname:
                return int(costs_map.get('conveyor', structure.getCost()))
        return int(structure.getCost())
    except Exception:
        try:
            return int(structure.getCost())
        except Exception:
            return 0
