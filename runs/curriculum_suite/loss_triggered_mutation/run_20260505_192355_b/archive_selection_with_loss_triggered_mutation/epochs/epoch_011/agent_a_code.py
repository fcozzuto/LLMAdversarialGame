def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if resources:
        best = None
        for tx, ty in resources:
            d = md(sx, sy, tx, ty)
            if best is None or (d, tx, ty) < best:
                best = (d, tx, ty)
        _, tx, ty = best
        dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
        best_move = None
        curd = md(sx, sy, tx, ty)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obst:
                continue
            nd = md(nx, ny, tx, ty)
            # Prefer moves that reduce distance; tie-break deterministically
            cand = (nd, dx, dy)
            if best_move is None or cand < best_move:
                best_move = cand
        if best_move is not None:
            _, dx, dy = best_move
            return [int(dx), int(dy)]

    # Fallback: move toward opponent while avoiding obstacles/bounds
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        # maximize separation after moving (deterministic)
        nd = md(nx, ny, ox, oy)
        cand = (-nd, dx, dy)
        if best_move is None or cand < best_move:
            best_move = cand
    if best_move is not None:
        _, dx, dy = best_move
        return [int(dx), int(dy)]
    return [0, 0]