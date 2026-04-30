def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def xy(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict):
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return int(q[0]), int(q[1])
        return None

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        q = xy(p)
        if q is not None:
            obstacles.add(q)

    resources = []
    for p in observation.get("resources", []) or []:
        q = xy(p)
        if q is not None and q not in obstacles:
            resources.append(q)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_val = 10**30

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            val = dist2(nx, ny, ox, oy)  # larger is better
            if (-val, dx, dy) < (-best_val, best_move[0], best_move[1]):
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = 10**30
        for rx, ry in resources:
            d = dist2(nx, ny, rx, ry)
            if d < nd:
                nd = d
        od = 10**30
        for rx, ry in resources:
            d = dist2(ox, oy, rx, ry)
            if d < od:
                od = d
        # Prefer closer to nearest resource; discourage moves that let opponent be much closer.
        val = nd * 100 - (od - nd) * 10
        if val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]