def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # Deterministic fallback: move toward the farther corner from the opponent
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (man(c[0], c[1], ox, oy), -man(c[0], c[1], sx, sy), c[0], c[1]))
        bestm = [0, 0]
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < bestd or (d == bestd and (dx, dy) < (bestm[0], bestm[1])):
                bestd = d
                bestm = [dx, dy]
        return bestm

    best_move = [0, 0]
    best_val = -10**18
    best_d = 10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        local_best = -10**18
        local_d = 10**9

        for rx, ry in resources:
            d1 = man(nx, ny, rx, ry)
            d2 = man(ox, oy, rx, ry)
            gap = d2 - d1  # positive means we can reach first
            # Strongly prioritize winning races for a resource; then prefer closer.
            if gap >= 0:
                v = 100000 + gap * 200 - d1
            else:
                v = gap * 200 - d1
            if v > local_best or (v == local_best and (d1 < local_d or (d1 == local_d and (rx, ry) < (0, 0)))):
                local_best = v
                local_d = d1

        if local_best > best_val or (local_best == best_val and (local_d < best_d or (local_d == best_d and (dx, dy) < (best_move[0], best_move[1])))):
            best_val = local_best
            best_d = local_d
            best_move = [dx, dy]

    return best_move