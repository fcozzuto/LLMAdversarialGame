def choose_move(observation):
    def pos(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (v[0], v[1])
        if isinstance(v, dict):
            for k in ("pos", "position", "loc", "location", "xy", "coord", "coords"):
                p = v.get(k)
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    return (p[0], p[1])
        return None

    def add_all(x):
        out = []
        if isinstance(x, dict):
            for v in x.values():
                p = pos(v)
                if p is not None:
                    out.append(p)
                elif isinstance(v, (list, tuple)):
                    for e in v:
                        p = pos(e)
                        if p is not None:
                            out.append(p)
        elif isinstance(x, (list, tuple)):
            for v in x:
                p = pos(v)
                if p is not None:
                    out.append(p)
        return out

    def sgn(v):
        return 1 if v > 0 else -1 if v < 0 else 0

    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    me = pos(observation.get("self_position")) or (0, 0)
    opp = pos(observation.get("opponent_position"))
    res = add_all(observation.get("resources"))
    obs = set(add_all(observation.get("obstacles")))
    if not res:
        if opp is not None:
            dx = sgn(opp[0] - me[0])
            dy = sgn(opp[1] - me[1])
            cand = [(dx, dy), (dx, 0), (0, dy), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
        else:
            cand = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0)]
    else:
        best = min(res, key=lambda p: (abs(p[0] - me[0]) + abs(p[1] - me[1]), abs(p[0] - me[0]), abs(p[1] - me[1]), p[0], p[1]))
        dx = sgn(best[0] - me[0])
        dy = sgn(best[1] - me[1])
        cand = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
        if opp is not None and abs(opp[0] - me[0]) + abs(opp[1] - me[1]) <= 2:
            cand = [(dx, dy), (dx, 0), (0, dy)] + cand

    for dx, dy in cand:
        nx, ny = me[0] + dx, me[1] + dy
        if (dx, dy) == (0, 0) or (0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs):
            return [int(dx), int(dy)]
    return [0, 0]
