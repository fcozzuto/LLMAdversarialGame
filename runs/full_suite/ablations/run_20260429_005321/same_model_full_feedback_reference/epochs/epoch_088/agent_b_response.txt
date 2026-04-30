def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    # If no resources visible, drift away from opponent toward safer diagonal.
    if not resources:
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not legal(nx, ny):
                    continue
                # Prefer maximizing distance to opponent; tie-break lexicographically.
                score = dist2(nx, ny, ox, oy)
                cand = (score, -dx, -dy, dx, dy)
                if best is None or cand > best:
                    best = cand
        return [best[3], best[4]] if best else [0, 0]

    # Score each immediate move by:
    # - closeness to the nearest remaining resource (primary, lower is better)
    # - ability to approach: reduce distance-to-resources monotonically vs current
    # - keep distance from opponent to reduce contesting (secondary)
    cur_best_res = min(dist2(sx, sy, rx, ry) for rx, ry in resources)
    best_move = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        dres = min(dist2(nx, ny, rx, ry) for rx, ry in resources)
        # Encourage progress (positive if we improved)
        progress = cur_best_res - dres
        # After-move separation from opponent (higher is better)
        sep = dist2(nx, ny, ox, oy)
        # Also penalize moving into opponent "direction" roughly by dot product
        vx1, vy1 = nx - sx, ny - sy
        vx2, vy2 = ox - sx, oy - sy
        dot = vx1 * vx2 + vy1 * vy2

        # Primary: minimize dres, then maximize progress, then maximize sep, then avoid moving toward opponent
        score = ( -dres, progress, sep, -dot )
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])] if best_move else [0, 0]