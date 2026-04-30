def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    cx, cy = w // 2, h // 2

    def score_cell(nx, ny):
        # Prefer getting to resources where we are relatively closer than opponent.
        best = None
        for rx, ry in resources:
            sd = dist2(nx, ny, rx, ry)
            od = dist2(ox, oy, rx, ry)
            # We want maximize (od - sd); also break ties by absolute closeness.
            key = (od - sd, -(sd + dist2(sx, sy, rx, ry) * 0), -sd, -abs(rx - cx) - abs(ry - cy))
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        if best is not None:
            return best[0][0] * 1000 + best[0][1] * 10 + best[0][2]
        # No resources: drift to center while not moving toward obstacles too directly.
        return -dist2(nx, ny, cx, cy) - min(dist2(nx, ny, ox2, oy2) for (ox2, oy2) in obstacles) if obstacles else -dist2(nx, ny, cx, cy)

    # Choose move maximizing deterministic heuristic; tie-break by fixed direction order.
    best_mv = (0, 0)
    best_sc = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = score_cell(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)
    return [int(best_mv[0]), int(best_mv[1])]