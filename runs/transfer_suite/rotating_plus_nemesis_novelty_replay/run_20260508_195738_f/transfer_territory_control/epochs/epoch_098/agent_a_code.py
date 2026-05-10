def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp_t = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    un = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    nbrs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def step_score(nx, ny):
        # Prefer moves that (1) reduce distance to opponent-claimed border,
        # (2) increase pressure by moving into/adjacent to opponent territory or unclaimed near it,
        # (3) avoid obstacles and avoid oscillations.
        if not inb(nx, ny) or (nx, ny) in obs:
            return -10**9
        man_op = min(abs(nx - ox) + abs(ny - oy) for (ox, oy) in opp_t) if opp_t else 99
        adj_opp = any(inb(nx + dx, ny + dy) and (nx + dx, ny + dy) in opp_t for dx, dy in nbrs if (dx, dy) != (0, 0))
        adj_unopp = any(inb(nx + dx, ny + dy) and ((nx + dx, ny + dy) in un) for dx, dy in nbrs if (dx, dy) != (0, 0))
        dist_self = abs(nx - sx) + abs(ny - sy)
        stay_pen = 1 if (nx, ny) == (sx, sy) else 0
        on_self = 1 if (nx, ny) in selft else 0
        on_opp = 1 if (nx, ny) in opp_t else 0
        # Encourage entering opponent cells (flipping on entry)
        return (200 if on_opp else 0) + (80 if adj_opp else 0) + (30 if adj_unopp else 0) - (3 * man_op) + (2 * on_self) - dist_self - (5 * stay_pen)

    # Primary policy: choose best immediate step toward opponent pressure border.
    best = None
    bestv = -10**18
    for dx, dy in nbrs:
        nx, ny = sx + dx, sy + dy
        v = step_score(nx, ny)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    # Fallback: if all blocked, stay (engine will keep in place, deterministic).
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]