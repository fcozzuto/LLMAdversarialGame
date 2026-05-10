def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    targets = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = (-(10**9), 0, 0)
    if targets:
        tx, ty = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            s = - (abs(nx - tx) + abs(ny - ty))
            if (nx, ny) in unclaimed:
                s += 1
            s += -0.05 * (abs(nx - ox) + abs(ny - oy))
            if s > best[0]:
                best = (s, dx, dy)
        return [best[1], best[2]]

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            s = - (abs(nx - tx) + abs(ny - ty))
            s += 2 if (nx, ny) in unclaimed else 0
            s += -0.05 * (abs(nx - ox) + abs(ny - oy))
            if s > best[0]:
                best = (s, dx, dy)
        return [best[1], best[2]]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        s = - (abs(nx - cx) + abs(ny - cy))
        s += -0.05 * (abs(nx - ox) + abs(ny - oy))
        if s > best[0]:
            best = (s, dx, dy)
    return [best[1], best[2]]