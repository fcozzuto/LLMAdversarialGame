def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                resources.append((x, y))

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    candidates = [(dx, dy) for (dx, dy) in deltas if inside(sx + dx, sy + dy)]
    if not candidates:
        return [0, 0]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Score heuristic:
    # - Prefer moves that reduce distance to the nearest resource.
    # - If no resources, prefer moving toward center while discouraging close contact with opponent.
    if resources:
        best = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            mind = min(dist2(nx, ny, rx, ry) for rx, ry in resources)
            score = (mind, dist2(nx, ny, ox, oy))  # tie-break away from opponent a bit
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        to_center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        away_from_op = dist2(nx, ny, ox, oy)
        score = (to_center, -away_from_op)  # minimize center distance; maximize opponent distance
        if best is None or score < best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]