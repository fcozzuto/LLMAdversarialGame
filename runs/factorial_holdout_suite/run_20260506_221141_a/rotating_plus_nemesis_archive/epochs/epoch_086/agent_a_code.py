def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Move toward the farthest resource corner deterministically if none visible
        target = (w - 1, h - 1) if (w - 1 - sx) + (h - 1 - sy) >= (sx) + (sy) else (0, 0)
        tx, ty = target
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy  # engine would keep in place; still evaluate as staying
        total = 0.0
        # Greedy advantage: aim at resources where we are closer than opponent
        for rx, ry in resources:
            myd = abs(rx - nx) + abs(ry - ny)
            opd = abs(rx - ox) + abs(ry - oy)
            # Prefer collecting; penalize resources where opponent is closer
            total += 1.0 / (myd + 1.0) - 1.3 / (opd + 1.0)
            # Slight preference for nearer resources overall
            total += 0.02 * (opd - myd)
        # Prefer not to stay if a valid improving move exists
        if dx == 0 and dy == 0:
            total -= 0.01
        if total > best_val:
            best_val = total
            best = (dx, dy)

    return [int(best[0]), int(best[1])]