def choose_move(observation):
    px, py = observation.get('self_position', (0, 0))
    ox, oy = observation.get('opponent_position', (px, py))
    resources = observation.get('resources', [])
    territory_targets = observation.get('territory_targets', [])
    
    # Seek nearest resource
    if resources:
        res = min(resources, key=lambda r: abs(r[0]-px)+abs(r[1]-py))
        dx = 0 if res[0] == px else (1 if res[0] > px else -1)
        dy = 0 if res[1] == py else (1 if res[1] > py else -1)
        if dx in [-1, 0, 1] and dy in [-1, 0, 1]:
            return [dx, dy]
    # Seek nearest territory target
    if territory_targets:
        tgt = min(territory_targets, key=lambda t: abs(t[0]-px)+abs(t[1]-py))
        dx = 0 if tgt[0] == px else (1 if tgt[0] > px else -1)
        dy = 0 if tgt[1] == py else (1 if tgt[1] > py else -1)
        if dx in [-1, 0, 1] and dy in [-1, 0, 1]:
            return [dx, dy]
    # Pursue opponent
    if ox != px or oy != py:
        dx = 0 if ox == px else (1 if ox > px else -1)
        dy = 0 if oy == py else (1 if oy > py else -1)
        return [dx, dy]
    # Stay still if no info
    return [0, 0]
