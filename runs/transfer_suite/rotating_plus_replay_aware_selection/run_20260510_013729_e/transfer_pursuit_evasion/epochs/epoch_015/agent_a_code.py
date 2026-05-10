def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ob.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    pursuer = "pursuer" in role

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in ob

    def manh(x, y):
        return abs(x - ox) + abs(y - oy)

    # If pursuer: 1-step minimax (opponent tries to maximize distance)
    if pursuer:
        best = None
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            if nx == ox and ny == oy:
                return [dx, dy]
            worst = -1
            # opponent move (evader): maximize distance
            for odx, ody in deltas:
                px, py = ox + odx, oy + ody
                if not valid(px, py):
                    continue
                d = abs(nx - px) + abs(ny - py)
                if d > worst:
                    worst = d
            val = -worst  # minimize worst distance
            if best is None or val > best_val or (val == best_val and (dx, dy) < best):
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # If evader: maximize distance with simple obstacle-aware tie-break
    best = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = manh(nx, ny)
        # prefer moves that also avoid being "cornered" (more free adjacent cells)
        free = 0
        for adx, ady in deltas:
            ax, ay = nx + adx, ny + ady
            if valid(ax, ay):
                free += 1
        val = (d * 10) + free
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = [dx, dy]
    return best