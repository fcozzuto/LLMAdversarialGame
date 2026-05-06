def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_row = [p for p in res if p[1] == oy]
    candidates = opp_row if opp_row else res

    best = None
    for tx, ty in candidates:
        myd = abs(tx - sx) + abs(ty - sy)
        opd = abs(tx - ox) + abs(ty - oy)
        # Deny opponent's row when possible; otherwise choose maximal advantage.
        if opp_row:
            key = (-myd, -opd)  # take closest on their row first
        else:
            key = (opd - myd, -myd, -tx, -ty)  # win contests, then shorten path
        if best is None or key > best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    def sign(v):
        return 1 if v > 0 else (-1 if v < 0 else 0)

    moves = []
    dx = sign(tx - sx)
    dy = sign(ty - sy)
    moves.append((dx, dy))
    moves.append((dx, 0))
    moves.append((0, dy))
    moves.append((dx, -dy))
    moves.append((0, 0))

    for ndx, ndy in moves:
        nx, ny = sx + ndx, sy + ndy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [int(ndx), int(ndy)]
    return [0, 0]