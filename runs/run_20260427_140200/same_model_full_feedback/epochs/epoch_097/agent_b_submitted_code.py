def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    best = None
    if resources:
        for (tx, ty) in resources:
            d = abs(sx - tx) + abs(sy - ty)
            if best is None or d < best[0] or (d == best[0] and (tx, ty) < best[1]):
                best = (d, (tx, ty))
        tx, ty = best[1]
        curd = abs(sx - tx) + abs(sy - ty)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nd = abs(nx - tx) + abs(ny - ty)
            if nd < curd or (nd == curd and (dx, dy) < (best_move[0], best_move[1]) if best_move else True):
                pass
        # deterministic selection by minimizing nd then direction order
        best_move = None
        curd = abs(sx - tx) + abs(sy - ty)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nd = abs(nx - tx) + abs(ny - ty)
            cand = (nd, dx, dy)
            if best_move is None or cand < best_move:
                best_move = cand
        return [best_move[1], best_move[2]]

    # No resources: move toward a corner opposite the opponent, avoiding obstacles
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = min(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), c[0], c[1]))
    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = abs(nx - tx) + abs(ny - ty)
        cand = (nd, dx, dy)
        if best_move is None or cand < best_move:
            best_move = cand
    if best_move is None:
        return [0, 0]
    return [best_move[1], best_move[2]]