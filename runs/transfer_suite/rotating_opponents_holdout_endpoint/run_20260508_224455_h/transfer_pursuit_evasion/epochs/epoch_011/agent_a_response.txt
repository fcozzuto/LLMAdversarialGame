def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles
    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic order bias toward staying + main axis, then toward increasing x, then y
    moves = sorted(moves, key=lambda d: (d == (0, 0), abs(d[0]) + abs(d[1]) == 2, d[0] < 0, d[1] < 0, d[0], d[1]))

    role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_evader = any(k in role for k in ("evader", "evade", "escape", "runner"))
    opp_evader = any(k in opp_role for k in ("evader", "evade", "escape", "runner"))
    we_evader = self_evader and not opp_evader

    def neigh_count(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if inb(nx, ny) and not blocked(nx, ny):
                    c += 1
        return c

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = dist2(nx, ny)
        mc = neigh_count(nx, ny)
        if we_evader:
            # maximize distance; also keep mobility; small penalty for moving closer on manhattan
            md = abs(nx - ox) + abs(ny - oy)
            key = (d, mc, md)
            # prefer larger key
            key = tuple(-v for v in key[:-1]) + (key[-1],)  # wrong sign on md; fix below
        else:
            key = ( -d, mc, -(abs(nx - ox) + abs(ny - oy)) )
        if we_evader:
            key = (d, mc, -(abs(nx - ox) + abs(ny - oy)))
        if best is None or key > best_key:
            best_key = key
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best