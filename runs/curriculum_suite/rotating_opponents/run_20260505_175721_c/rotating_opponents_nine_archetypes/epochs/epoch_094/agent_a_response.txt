def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    (sx, sy) = observation.get("self_position", (0, 0)) or (0, 0)
    (ox, oy) = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def sign(a):
        return 1 if a > 0 else (-1 if a < 0 else 0)

    # Choose resource where we have the best "win" margin; tie-break by nearer to us.
    best = None
    best_key = None
    for tx, ty in resources:
        d1 = cheb(sx, sy, tx, ty)
        d2 = cheb(ox, oy, tx, ty)
        # Prefer we arrive strictly earlier; also prefer smaller (d1-d2) and proximity.
        key = (d1 - d2, d1, abs(tx - (w - 1 - ox)) + abs(ty - (h - 1 - oy)))
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    dx = sign(tx - sx)
    dy = sign(ty - sy)

    # Deterministic move selection with obstacle avoidance.
    candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy), (0, 0)]
    # If opponent is closer to our chosen target, bias stepping to increase distance from them.
    if cheb(ox, oy, tx, ty) < cheb(sx, sy, tx, ty):
        candidates = [(dx, dy), (dx, 0), (0, dy), (-dx, 0), (0, -dy), (-dx, dy), (dx, -dy), (0, 0)]

    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if inb(nx, ny):
            return [mx, my]
    return [0, 0]