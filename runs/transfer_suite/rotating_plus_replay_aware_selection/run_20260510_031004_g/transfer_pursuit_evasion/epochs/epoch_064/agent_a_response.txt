def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = None
    if "purs" in self_role:
        is_pursuer = True
    elif "evad" in self_role:
        is_pursuer = False
    if is_pursuer is None:
        if "purs" in opp_role:
            is_pursuer = False
        elif "evad" in opp_role:
            is_pursuer = True
    if is_pursuer is None:
        is_pursuer = True

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def clamp_in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_in_bounds(nx, ny):
            continue
        d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Prefer moving toward opponent if pursuer; away if evader.
        val = d if is_pursuer else -d

        # Mild obstacle proximity penalty to avoid getting boxed in.
        prox = 0
        for (bx, by) in obstacles:
            dd = abs(nx - bx) + abs(ny - by)
            if dd == 1:
                prox += 3
            elif dd == 2:
                prox += 1
        val -= prox if is_pursuer else -prox

        # Deterministic tie-breaker: lexicographic on move.
        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]