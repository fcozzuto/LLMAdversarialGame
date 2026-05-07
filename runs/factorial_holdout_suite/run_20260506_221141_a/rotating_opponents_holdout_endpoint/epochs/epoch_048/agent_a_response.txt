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

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose resource we can reach first; if tied, choose one that maximizes slack over opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if best_key is None or (ds < best_key[0]) or (ds == best_key[0] and (do - ds) > best_key[1]) or (ds == best_key[0] and (do - ds) == best_key[1] and (rx + ry) < best_key[2]):
            best_key = (ds, do - ds, rx + ry)
            best = (rx, ry)

    rx, ry = best
    if sx == rx and sy == ry:
        # Nudge toward nearest remaining resource if standing on it
        # (deterministic: pick smallest cheb then lex)
        best2 = None
        best2d = None
        for tx, ty in resources:
            d = cheb(sx, sy, tx, ty)
            if best2d is None or d < best2d or (d == best2d and (tx, ty) < best2):
                best2d = d
                best2 = (tx, ty)
        rx, ry = best2

    def sgn(v):
        if v > 0: return 1
        if v < 0: return -1
        return 0

    dx = sgn(rx - sx)
    dy = sgn(ry - sy)

    nx, ny = sx + dx, sy + dy
    if valid(nx, ny):
        return [dx, dy]

    # If blocked, try deterministic fallback among valid neighbor moves that reduce distance to target.
    neighbors = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_d = cheb(sx, sy, rx, ry)
    bestm = [0, 0]
    bestdm = None
    for mdx, mdy in neighbors:
        tx, ty = sx + mdx, sy + mdy
        if not valid(tx, ty):
            continue
        nd = cheb(tx, ty, rx, ry)
        score = (nd - cur_d, abs(tx - ox) + abs(ty - oy), tx, ty)
        if bestdm is None or score < bestdm:
            bestdm = score
            bestm = [mdx, mdy]
    return bestm