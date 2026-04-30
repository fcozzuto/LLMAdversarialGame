def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Deterministically pick a "focus" resource: nearest to self (tie -> lexicographically).
    focus = None
    if resources:
        best_d = None
        for rx, ry in resources:
            d = dist2(sx, sy, rx, ry)
            if best_d is None or d < best_d or (d == best_d and (rx, ry) < focus):
                best_d = d
                focus = (rx, ry)

    # If no resources, head toward center (deterministic).
    if focus is None:
        target = (w // 2, h // 2)
    else:
        target = focus

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Goal: be closer to target than opponent, while not allowing opponent to be too close to us.
        myd = dist2(nx, ny, target[0], target[1])
        opd = dist2(ox, oy, target[0], target[1])

        # Safety: keep distance from opponent (prefer moving that increases it).
        sd = dist2(nx, ny, ox, oy)
        cur_sd = dist2(sx, sy, ox, oy)

        # Tie-break toward movement direction that reduces my distance to target, then toward increasing safety.
        val = 1000.0 * (opd - myd) + 10.0 * (sd - cur_sd) - 0.001 * (abs(dx) + abs(dy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]