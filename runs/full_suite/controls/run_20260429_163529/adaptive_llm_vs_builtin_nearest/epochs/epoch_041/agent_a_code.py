def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w // 2), (h // 2)
        best = (0, 0)
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                d = cheb(nx, ny, tx, ty)
                if d < bestd or (d == bestd and (dx, dy) < best):
                    bestd, best = d, (dx, dy)
        return [best[0], best[1]]

    best_res = None
    best_key = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # higher means opponent is farther (better chance for us)
        key = (lead, -ds, -rx, -ry)  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res
    best = (0, 0)
    best_cost = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # encourage closing toward target while discouraging squares where opponent would be closer next
        cost = d_self + (0 if d_self <= d_opp else 1) + (1 if (nx, ny) in resources else 0)
        if best_cost is None or cost < best_cost or (cost == best_cost and (dx, dy) < best):
            best_cost = cost
            best = (dx, dy)

    if best_cost is None:
        # fallback: move to reduce distance to chosen resource without obstacle constraints (still avoid obstacles)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                best = (dx, dy)
                break
    return [best[0], best[1]]