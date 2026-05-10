def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unT = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count(x, y, S):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in S:
                    c += 1
        return c

    # Pick a strategic target: unclaimed cells most adjacent to opponent territory, else fallback.
    targets = list(unT)
    best_target = None
    best_key = None
    for x, y in targets:
        d = abs(x - sx) + abs(y - sy)
        a = adj_count(x, y, opT)
        # Prefer adjacency "frontier" moves.
        key = (-a, d, y, x)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (x, y)

    if best_target is None:
        # If no unclaimed, aim at opponent territory adjacency cells by heading to opponent.
        best_target = (ox, oy)

    tx, ty = best_target

    # Evaluate candidate next moves.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        on_op = 1 if (nx, ny) in opT else 0
        on_un = 1 if (nx, ny) in unT else 0
        on_self = 1 if (nx, ny) in selfT else 0
        frontier = adj_count(nx, ny, opT)
        # Strongly reward counter-claiming by entering opponent territory.
        score = (200 * on_op + 40 * on_un + 5 * on_self) + 8 * frontier - 0.5 * dist
        # Slightly prefer moves that don't drift away from the opponent overall.
        score += -0.05 * (abs(nx - ox) + abs(ny - oy))
        cand.append(((score, -frontier, dist, nx, ny), (dx, dy)))

    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: t[0])  # deterministic tie-break via tuple
    return [int(cand[0][1][0]), int(cand[0][1][1])]