def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            pos = r.get("pos")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                resources.append((int(pos[0]), int(pos[1])))
            else:
                x = r.get("x")
                y = r.get("y")
                if x is not None and y is not None:
                    resources.append((int(x), int(y)))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        best = None
        best_key = None
        for (rx, ry) in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; tie-break with absolute distance to us.
            key = (do - ds, -ds)
            if best is None or key > best_key:
                best = (rx, ry)
                best_key = key
        return best

    tx, ty = best_target()

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        # Add tactical pressure: if opponent can also get closer quickly, avoid letting them take it uncontested.
        do_now = cheb(ox, oy, tx, ty)
        val = (ds2, do_now - ds2)  # smaller ds2; then larger advantage
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move == (0, 0):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                if (dx, dy) != (0, 0):
                    best_move = (dx, dy)
                    break
    return [int(best_move[0]), int(best_move[1])]