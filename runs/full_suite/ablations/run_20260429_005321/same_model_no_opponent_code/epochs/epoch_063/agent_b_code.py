def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx * dx + dy * dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_tgt = None
    if resources:
        best_key = None
        for t in resources:
            d = dist2((sx, sy), t)
            do = dist2((ox, oy), t)
            # Prefer closer to us; bias toward points where opponent is farther.
            key = (d - do, d)
            if best_key is None or key < best_key:
                best_key = key
                best_tgt = t

    # If no resources, just drift away from opponent while staying valid.
    if best_tgt is None:
        best_key = None
        best_dir = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d0 = dist2((nx, ny), (ox, oy))
            key = (-d0, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_dir = (dx, dy)
        return [best_dir[0], best_dir[1]]

    best_score = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_res = dist2((nx, ny), best_tgt)
        d_opp = dist2((nx, ny), (ox, oy))
        # Higher is better: minimize distance to target, maximize distance from opponent.
        score = -d_res + (d_opp * 0.5)
        key = (-score, dx, dy)  # deterministic tie-break
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]