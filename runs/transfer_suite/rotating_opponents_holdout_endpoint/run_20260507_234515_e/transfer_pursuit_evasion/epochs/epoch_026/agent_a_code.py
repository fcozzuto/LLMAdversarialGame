def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    try:
        rs = observation.get("scores", {}) or {}
        me = rs.get("self", rs.get("me", 0))
        op = rs.get("opponent", rs.get("opp", rs.get("op", 0)))
    except Exception:
        me, op = 0, 1
    chase = me <= op

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in oset:
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        sc = -d2 if chase else d2
        if best_sc is None or sc > best_sc or (sc == best_sc and (dx, dy) == (0, 0)):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in oset:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]