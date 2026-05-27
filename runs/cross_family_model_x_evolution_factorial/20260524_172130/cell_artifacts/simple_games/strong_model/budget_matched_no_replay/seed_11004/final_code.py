def choose_move(observation):
    def pos(v):
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                return [v.get("x"), v.get("y")]
            for k in ("position", "pos", "loc", "location", "coord", "coordinates", "xy"):
                p = pos(v.get(k))
                if p is not None:
                    return p
        elif isinstance(v, (list, tuple)) and len(v) >= 2:
            if isinstance(v[0], (int, float)) and isinstance(v[1], (int, float)):
                return [v[0], v[1]]
        return None

    def clamp(d):
        return -1 if d < 0 else (1 if d > 0 else 0)

    me = None
    for k in ("self_position", "self", "me", "agent", "player"):
        me = pos(observation.get(k))
        if me is not None:
            break
    if me is None:
        me = [0, 0]

    opp = None
    for k in ("opponent_position", "opponent", "enemy"):
        opp = pos(observation.get(k))
        if opp is not None:
            break

    obs = observation.get("obstacles") or []
    res = observation.get("resources") or []
    best = None
    bd = None
    for t in res:
        p = pos(t)
        if p is None:
            continue
        d = abs(p[0] - me[0]) + abs(p[1] - me[1])
        if bd is None or d < bd:
            bd = d
            best = p

    if best is None and opp is not None:
        best = opp
    if best is None:
        w = observation.get("grid_width", 0)
        h = observation.get("grid_height", 0)
        best = [w // 2, h // 2] if w and h else [me[0] + 1, me[1]]

    dx = clamp(best[0] - me[0])
    dy = clamp(best[1] - me[1])

    if dx != 0 or dy != 0:
        nx, ny = me[0] + dx, me[1] + dy
        for o in obs:
            p = pos(o)
            if p is not None and p[0] == nx and p[1] == ny:
                if dx != 0:
                    dx, dy = 0, clamp(best[1] - me[1])
                elif dy != 0:
                    dx, dy = clamp(best[0] - me[0]), 0
                break

    if dx == 0 and dy == 0:
        if opp is not None:
            dx = -clamp(opp[0] - me[0])
            dy = -clamp(opp[1] - me[1])
        if dx == 0 and dy == 0:
            dx = 1
    return [dx, dy]
