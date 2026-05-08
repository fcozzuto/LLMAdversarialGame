def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    targets = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            targets.append((p[0], p[1]))
    if not targets:
        for p in (observation.get("unclaimed_cells") or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((p[0], p[1]))

    self_t = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    def best_target():
        if targets:
            return min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        return (ox, oy)

    tx, ty = best_target()

    def step_value(nx, ny):
        if not free(nx, ny):
            return -10**18
        d_self = abs(nx - sx) + abs(ny - sy)
        d_t = abs(nx - tx) + abs(ny - ty)
        invade = 1 if (nx, ny) in opp_t else 0
        defend = 1 if (nx, ny) in self_t else 0
        near_opp = 1 if max(abs(nx - ox), abs(ny - oy)) == 1 else 0
        # Prefer expanding/invading while still moving toward a target.
        return (10 * invade + 2 * near_opp + 0.5 * defend) - (d_t + 0.1 * d_self)

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = step_value(nx, ny)
        if v > bestv or (v == bestv and (best is None or (dx, dy) < best)):
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]