def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked

    moves = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]

    # sanitize resources to (x,y)
    targets = []
    for r in resources:
        if isinstance(r, dict):
            p = r.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        else:
            continue
        if legal(x, y):
            targets.append((x, y))

    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not targets:
        # drift toward center to avoid getting stuck on edges
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = (abs(nx - cx) + abs(ny - cy), abs(nx - ox) + abs(ny - oy))
            if bestv is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best

    # choose move that maximizes advantage over opponent to a chosen resource
    best_move = [0, 0]
    best_score = None
    # deterministic tie-breaker order: moves list already fixed (dy outer, dx inner)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_best = None
        my_best_d2 = None
        for tx, ty in targets:
            d_self = abs(nx - tx) + abs(ny - ty)
            d_opp = abs(ox - tx) + abs(oy - ty)
            # prefer resources where we are closer (or become closer) than opponent
            adv = d_opp - d_self
            # primary: maximize adv, secondary: minimize our distance after move, tertiary: deterministic
            key = (adv, -d_self)
            if my_best is None or key > my_best:
                my_best = key
                my_best_d2 = d_self
        # overall score: favor higher advantage; slight preference to reduce distance to avoid stalling
        overall = (my_best[0], -my_best_d2)
        if best_score is None or overall > best_score:
            best_score = overall
            best_move = [dx, dy]

    return best_move