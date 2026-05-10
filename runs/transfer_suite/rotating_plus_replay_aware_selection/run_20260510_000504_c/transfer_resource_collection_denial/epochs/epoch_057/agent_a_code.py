def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    width = int(observation.get("grid_width") or 8)
    height = int(observation.get("grid_height") or 8)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", p)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obstacles.add((int(q[0]), int(q[1])))
            else:
                if "x" in p and "y" in p:
                    obstacles.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", r)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                resources.append((int(q[0]), int(q[1])))
            else:
                if "x" in r and "y" in r:
                    resources.append((int(r["x"]), int(r["y"])))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (myd, -((opd - myd)), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        block_bonus = 0
        if cheb(nx, ny, ox, oy) <= 1:
            block_bonus = 1
        return (d, abs((tx - nx)) + abs((ty - ny)), -block_bonus, dx, dy)

    best_m = None
    best_ms = None
    for dx, dy in moves:
        ms = score_move(dx, dy)
        if best_ms is None or ms < best_ms:
            best_ms = ms
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]