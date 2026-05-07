def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (sx, sy):
            # allow staying if it's the only legal option later
            pass
        candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    # Choose a move that maximizes our advantage over opponent on a target resource,
    # with a small tie-break toward faster acquisition and toward reducing opponent access.
    best = None
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy

        best_target = None
        best_adv = None
        best_dist = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if best_adv is None or adv > best_adv or (adv == best_adv and ds < best_dist):
                best_adv = adv
                best_dist = ds
                best_target = (rx, ry)

        rx, ry = best_target
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)

        # extra shaping: prefer moves that also increase our margin against the current closest threat
        # (opponent tends to go for nearby resources).
        min_do = None
        for tx, ty in resources:
            dpt = cheb(ox, oy, tx, ty)
            if min_do is None or dpt < min_do:
                min_do = dpt

        score = (best_adv, -ds, -(min_do - do))
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]