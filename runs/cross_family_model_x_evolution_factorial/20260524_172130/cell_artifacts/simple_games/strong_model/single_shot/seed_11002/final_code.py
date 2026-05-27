def choose_move(observation):
    def pos(x):
        if isinstance(x, dict):
            for a, b in (("x", "y"), ("row", "col"), ("r", "c")):
                if a in x and b in x:
                    return [x[a], x[b]]
        if isinstance(x, (list, tuple)) and len(x) >= 2:
            return [x[0], x[1]]
        return None

    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    me = pos(observation.get("self_position")) or [0, 0]
    opp = pos(observation.get("opponent_position")) or [w, h]
    res = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    blocked = set()
    for p in obs:
        q = pos(p)
        if q: blocked.add((q[0], q[1]))

    best = None
    bd = 10**9
    for r in res:
        p = pos(r)
        if not p: 
            continue
        d = abs(p[0] - me[0]) + abs(p[1] - me[1])
        if d < bd:
            bd = d
            best = p

    moves = [(0, 1), (1, 0), (0, -1), (-1, 0), (0, 0)]
    if best is None:
        t = [w // 2, h // 2]
        if abs(opp[0] - me[0]) + abs(opp[1] - me[1]) <= 2:
            t = [me[0] + (me[0] - opp[0]), me[1] + (me[1] - opp[1])]
    else:
        t = best

    cand = []
    for dx, dy in moves:
        nx, ny = me[0] + dx, me[1] + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            d = abs(t[0] - nx) + abs(t[1] - ny)
            e = abs(opp[0] - nx) + abs(opp[1] - ny)
            cand.append((d, -e, -abs(dx) - abs(dy), dx, dy))
    if cand:
        cand.sort()
        return [cand[0][3], cand[0][4]]
    return [0, 0]
