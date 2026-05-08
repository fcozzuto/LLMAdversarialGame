def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = [0, 0]
    best_val = -10**18

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            opp_near_pen = -5 if man(nx, ny, ox, oy) <= 1 else 0
            # Choose the resource that best favors us on this step (not just nearest).
            local_best = -10**18
            for tx, ty in resources:
                sd = man(nx, ny, tx, ty)
                od = man(ox, oy, tx, ty)
                # Prefer cutting off opponent: large od (they are far) and small sd (we are close).
                v = (-sd) + 0.35 * od - (1.5 if sd == 0 and od == 0 else 0) - (0.15 * man(nx, ny, sx, sy))
                if v > local_best:
                    local_best = v
            val = local_best + opp_near_pen
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        # No visible resources: move to reduce distance to opponent's side (likely next spawns).
        targets = [(0, h - 1), (w - 1, 0), (w - 1, h - 1), (0, 0)]
        tx, ty = max(targets, key=lambda t: man(ox, oy, t[0], t[1]) - man(sx, sy, t[0], t[1]))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -man(nx, ny, tx, ty) + (0.05 * man(nx, ny, ox, oy))
            if v > best_val:
                best_val = v
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]