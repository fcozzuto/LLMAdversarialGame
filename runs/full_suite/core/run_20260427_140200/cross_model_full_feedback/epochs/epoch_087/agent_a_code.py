def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        tx, ty = min(resources, key=lambda p: abs(p[0] - mx) + abs(p[1] - my))
        def score_move(dx, dy):
            nx, ny = mx + dx, my + dy
            if not free(nx, ny):
                return (10**9, -10**9)
            dist_to_t = abs(nx - tx) + abs(ny - ty)
            dist_to_o = abs(nx - ox) + abs(ny - oy)
            return (dist_to_t, -dist_to_o)
        best = None
        for dx, dy in moves:
            s = score_move(dx, dy)
            if best is None or s < best[0]:
                best = (s, dx, dy)
        return [best[1], best[2]]

    # No visible resources: keep away from opponent if possible, else move safely toward center
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_dx, best_dy = 0, 0
    best_val = None
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not free(nx, ny):
            continue
        away = abs(nx - ox) + abs(ny - oy)
        toward_center = abs(nx - cx) + abs(ny - cy)
        val = (-away, toward_center, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_dx, best_dy = dx, dy
    return [best_dx, best_dy]