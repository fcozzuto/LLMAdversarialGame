def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can get first; if not, prefer those where we deny by being closer.
        priority = (od - sd, -(sd + 0.01 * (rx + 3 * ry)), -min(sd, od), rx, ry)
        if best is None or priority > best[0]:
            best = (priority, (rx, ry), sd, od)

    _, (tx, ty), sd, od = best

    # Step toward target (deterministic), with a simple obstacle fallback.
    dx = 0 if sx == tx else (1 if tx > sx else -1)
    dy = 0 if sy == ty else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if not blocked(nx, ny):
        return [dx, dy]

    # If diagonal blocked, try axis moves deterministically.
    cands = []
    if dx != 0:
        cands.append((dx, 0))
    if dy != 0:
        cands.append((0, dy))
    cands.append((0, 0))
    for mdx, mdy in cands:
        if not blocked(sx + mdx, sy + mdy):
            return [mdx, mdy]

    return [0, 0]