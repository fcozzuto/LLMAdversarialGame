def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles_list = observation.get("obstacles", [])
    obstacles = set()
    if isinstance(obstacles_list, list):
        for p in obstacles_list:
            if isinstance(p, list) or isinstance(p, tuple):
                if len(p) == 2:
                    obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    preferred_order = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neighbors(x, y):
        ns = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                ns.append((nx, ny))
        return ns if ns else [(x, y)]

    def sgn(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def cheb2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        ax, ay = abs(dx), abs(dy)
        return (ax if ax > ay else ay) ** 2

    # Immediate capture
    if inb(ox, oy):
        dx0, dy0 = ox - sx, oy - sy
        step = (sgn(dx0), sgn(dy0))
        if step in moves and (sx + step[0], sy + step[1]) == (ox, oy):
            return [step[0], step[1]]

    opp_moves = neighbors(ox, oy)

    best = None
    best_val = None
    for dx, dy in preferred_order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Opponent tries to maximize distance; we minimize the worst-case.
        worst = -1
        for ppx, ppy in opp_moves:
            # If opponent is caught (same cell), game ends; treat as worst for them = best for us
            if ppx == nx and ppy == ny:
                val = -10**9
            else:
                val = cheb2(nx, ny, ppx, ppy)
            if val > worst:
                worst = val
        # Prefer lower worst-case distance; tie-break with closer current distance to opponent.
        tie = cheb2(nx, ny, ox, oy)
        cand = (worst, tie)
        if best_val is None or cand < best_val:
            best_val = cand
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]