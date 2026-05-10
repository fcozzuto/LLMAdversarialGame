def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles
    def dist2(x, y): dx = x - ox; dy = y - oy; return dx * dx + dy * dy
    def manh(x, y): return abs(x - ox) + abs(y - oy)
    def neigh_count(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0: continue
                nx, ny = x + ddx, y + ddy
                if inb(nx, ny) and not blocked(nx, ny):
                    c += 1
        return c

    role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_evader = any(k in role for k in ("evader", "evade", "escape", "runner"))
    opp_evader = any(k in opp_role for k in ("evader", "evade", "escape", "runner"))
    we_evader = self_evader and not opp_evader

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic tie-breaking preference order
    moves.sort(key=lambda d: (d[0] == 0 and d[1] == 0, abs(d[0]) + abs(d[1]) == 2, d[0], d[1]))

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        d2 = dist2(nx, ny)
        dm = manh(nx, ny)
        nc = neigh_count(nx, ny)

        if we_evader:
            # maximize distance, avoid dead-ends, keep momentum away from opponent
            val = d2 * 10 - dm * 2 + (nc * 3) - (0 if nc >= 3 else (8 - nc) * 2)
        else:
            # minimize distance, avoid corners trapping ourselves behind obstacles
            val = -d2 * 10 - dm * 2 + (nc * 3) - (0 if nc >= 3 else (8 - nc) * 2)

        if best is None or (val > best_val):
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]