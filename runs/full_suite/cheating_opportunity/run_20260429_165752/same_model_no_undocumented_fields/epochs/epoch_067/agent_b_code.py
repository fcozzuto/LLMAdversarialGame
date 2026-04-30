def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not free(sx, sy):
        for dx, dy in moves:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    # Choose nearest resource by Chebyshev distance; tie-break deterministically by coordinates.
    if resources:
        best_t = None
        best_td = None
        for (rx, ry) in resources:
            d = max(abs(rx - sx), abs(ry - sy))
            if best_t is None or d < best_td or (d == best_td and (rx, ry) < best_t):
                best_t = (rx, ry)
                best_td = d
        tx, ty = best_t
    else:
        tx, ty = w - 1, h - 1  # deterministic fallback

    def score_move(nx, ny):
        # Move objective: reduce distance to target, avoid opponent contact, avoid stagnation.
        if (nx, ny) in obstacles:
            return -10**9
        d_to_t = max(abs(tx - nx), abs(ty - ny))
        d_to_o = max(abs(ox - nx), abs(oy - ny))
        # If we are capturing/blocking: being closer to target is primary.
        # Opponent avoidance is secondary; if we can "race" on same line, keep small penalty.
        race_line = (tx == ox or ty == oy) or (tx - ox == 0 and ty - oy == 0)
        opp_pen = 0 if race_line else (1.8 / (d_to_o + 1))
        center_bias = -0.02 * (abs((w - 1) / 2 - nx) + abs((h - 1) / 2 - ny))
        # Prefer staying only if it doesn't worsen target distance.
        stay_pen = 0.05 if (nx == sx and ny == sy) else 0.0
        return -d_to_t - opp_pen + center_bias - stay_pen

    best_val = -10**18
    best_move = (0, 0)
    # Deterministic tie-break by move order in list.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        v = score_move(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]