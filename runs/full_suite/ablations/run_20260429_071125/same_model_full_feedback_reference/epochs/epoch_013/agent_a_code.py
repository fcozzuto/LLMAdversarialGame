def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Strategy: target a resource where we can arrive no later than opponent; otherwise head toward closest.
    best_dxdy = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate best resource for this move
        local_best = -10**9
        min_ours = 10**9
        for rx, ry in resources:
            d_our = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            if d_our < min_ours:
                min_ours = d_our
            # If we can beat opponent (or tie), prioritize; otherwise discourage.
            advantage = d_opp - d_our
            val = advantage * 100 - d_our
            # Slight preference for resources closer to opponent's side (to reduce their leverage)
            val -= (d_opp > d_our) * (d_opp - d_our)
            if val > local_best:
                local_best = val

        # If no contested advantage, fall back to closest resource
        fallback = -min_ours
        candidate = local_best + (0 if local_best > -10**8 else fallback)

        if best_val is None or candidate > best_val:
            best_val = candidate
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]