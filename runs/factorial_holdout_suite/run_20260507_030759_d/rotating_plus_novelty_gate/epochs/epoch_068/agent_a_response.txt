def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    obstacles = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    resources = observation.get("resources", []) or []
    resources = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]
    resset = set(resources)

    if (sx, sy) in resset:
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 if d1 >= d2 else d2

    best = None
    best_key = None
    for i, (rx, ry) in enumerate(resources):
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Intercept: prioritize resources where we can beat opponent; otherwise block near-term.
        margin = od - sd  # positive is good for us
        key = (-margin, sd + (0 if margin > 0 else 2), i)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Move to neighbor that minimizes our distance to target; tie-break toward actions that keep distance from opponent.
    best_move = (0, 0)
    best_d = None
    best_opd = None
    for mdx, mdy in legal:
        nx, ny = sx + mdx, sy + mdy
        if (nx, ny) in resset:
            return [mdx, mdy]
        d = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)
        if best_d is None or d < best_d or (d == best_d and opd > best_opd) or (d == best_d and opd == best_opd and (mdx, mdy) < best_move):
            best_d = d
            best_opd = opd
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]