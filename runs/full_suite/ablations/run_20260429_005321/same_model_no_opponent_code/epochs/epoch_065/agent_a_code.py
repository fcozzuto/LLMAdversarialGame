def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)

    def norm_pos(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return (int(p[0]), int(p[1]))
        if isinstance(p, dict) and "x" in p and "y" in p:
            return (int(p["x"]), int(p["y"]))
        return None

    obs = set()
    for p in (observation.get("obstacles") or []):
        q = norm_pos(p)
        if q is not None:
            obs.add(q)

    res = []
    for p in (observation.get("resources") or []):
        q = norm_pos(p)
        if q is not None and q not in obs:
            res.append(q)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not res:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (ds, -do, rx, ry)  # tie-break deterministically
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((cheb(nx, ny, tx, ty), abs(dx) + abs(dy), dx, dy))
    moves.sort()

    if moves:
        return [moves[0][2], moves[0][3]]

    if inb(sx, sy) and (sx, sy) not in obs:
        return [0, 0]
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
    return [0, 0]