def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cell_value(x, y):
        if not resources:
            # drift toward center if no resources
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            return -((x - cx) * (x - cx) + (y - cy) * (y - cy))
        # Higher is better: advantage over opponent + slight center bias
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -0.02 * ((x - cx) * (x - cx) + (y - cy) * (y - cy))
        best = -10**9
        for tx, ty in resources:
            sd = md(x, y, tx, ty)
            od = md(ox, oy, tx, ty)
            # Prefer resources we can reach earlier; tie-break by self distance
            val = (od - sd) * 1.6 - sd * 0.12 + center_bias
            if val > best:
                best = val
        return best

    if not resources:
        # no targets: try to move toward center while avoiding obstacles
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tx = 0 if sx == int(round(cx)) else (1 if sx < cx else -1)
        ty = 0 if sy == int(round(cy)) else (1 if sy < cy else -1)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if legal(nx, ny) and dx == tx and dy == ty:
                    return [dx, dy]
        return [0, 0]

    # Evaluate all legal moves with one-ply lookahead
    best_move = [0, 0]
    best_val = -10**18
    best_tiebreak = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = cell_value(nx, ny)
        t = (-(abs(nx - ox) + abs(ny - oy)), abs(nx - sx) + abs(ny - sy), dx, dy)
        if v > best_val or (v == best_val and (best_tiebreak is None or t < best_tiebreak)):
            best_val = v
            best_tiebreak = t
            best_move = [dx, dy]
    return best_move