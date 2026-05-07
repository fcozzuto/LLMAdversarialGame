def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def clamp(x, lo, hi):
        return lo if x < lo else (hi if x > hi else x)

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            nx = clamp(nx, 0, w - 1)
            ny = clamp(ny, 0, h - 1)
            if (nx, ny) in obstacles:
                continue
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # One-step lookahead: pick move that improves our advantage over opponent for the best remaining resource.
    best = None
    best_val = None
    for dx, dy, nx, ny in moves:
        # Deny effect: staying closer to opponent reduces their ability to get "our" targets.
        deny = -5.0 * (cheb(nx, ny, ox, oy) <= 1)

        # Evaluate best resource after move.
        local_best = None
        local_max = None
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer resources where we can arrive not later than opponent.
            # Cheaper (closer) resources get higher value; tie-break via advantage.
            val = (do - ds) * 10.0 - ds * 1.5
            if (local_max is None) or (val > local_max) or (val == local_max and (local_best is None or (tx, ty) < local_best)):
                local_max = val
                local_best = (tx, ty)
        score = local_max + deny
        # Deterministic tie-break: lexicographic move preference.
        cand = (score, -abs(dx) - abs(dy), dx, dy)
        if (best_val is None) or (cand > best_val):
            best_val = cand
            best = [dx, dy]
    return best