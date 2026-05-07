def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    my_turn = int(observation.get("turn_index", 0) or 0)
    aggressive = 1 if (observation.get("turns_remaining", 0) or 0) < 20 else 0
    # Prefer resources where we can arrive strictly sooner; then maximize lead; then closeness.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        lead = opd - myd
        # If we can't beat opponent, deprioritize heavily.
        if lead < 0:
            key = (-1000 + lead, -myd, myd)
        else:
            key = (lead + aggressive, -myd, myd)
        # Deterministic tie-break by coordinates
        key = (key[0], key[1], key[2], rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
        # Deterministic fallback: try orthogonal moves that reduce distance.
        options = []
        for tx, ty in ((dx, 0), (0, dy), (0, 0), (-dx, 0), (0, -dy)):
            nnx, nny = sx + tx, sy + ty
            if 0 <= nnx < w and 0 <= nny < h and (nnx, nny) not in obstacles:
                options.append((tx, ty))
        if options:
            # choose option minimizing our distance to target, then lexicographic
            options.sort(key=lambda m: (cheb(sx + m[0], sy + m[1], rx, ry), m[0], m[1]))
            dx, dy = options[0]
        else:
            dx, dy = 0, 0

    return [int(dx), int(dy)]