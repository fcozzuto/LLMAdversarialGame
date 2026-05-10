def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", None) or []
    obstacles_in = observation.get("obstacles", None) or []
    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    best_move = (0, 0)
    best_val = None

    if resources:
        best_tx, best_ty = None, None
        best_self = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                tx, ty = r[0], r[1]
                d = man(sx, sy, tx, ty)
                if best_self is None or d < best_self:
                    best_self, best_tx, best_ty = d, tx, ty
        tx, ty = best_tx, best_ty
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            sdist = man(nx, ny, tx, ty)
            odist = man(ox, oy, tx, ty)
            val = -sdist
            if sdist < odist:
                val += 1000 - sdist
            if sdist == odist:
                val -= 10
            val -= 2 * man(nx, ny, ox, oy)
            if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val, best_move = val, (dx, dy)
        if best_val is not None:
            return [best_move[0], best_move[1]]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        val = -(abs(nx - cx) + abs(ny - cy))
        val -= 2 * man(nx, ny, ox, oy)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)
    return [best_move[0], best_move[1]]