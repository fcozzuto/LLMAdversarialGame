def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in (observation.get("obstacles") or []):
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        elif isinstance(a, dict) and "x" in a and "y" in a:
            x, y = int(a["x"]), int(a["y"])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist_diag_manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves2 = [m for m in moves if m != (0, 0)] + [(0, 0)]
    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in moves2:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Racing heuristic: pick the resource where we maximize (opponent dist - our dist),
        # i.e., where we can arrive sooner; tie-break by absolute our dist.
        local_best = -10**9
        local_tie = 10**9
        for rx, ry in resources:
            sd = dist_diag_manh(nx, ny, rx, ry)
            od = dist_diag_manh(ox, oy, rx, ry)
            val = od - sd
            if val > local_best or (val == local_best and sd < local_tie) or (val == local_best and sd == local_tie and (rx + ry) < (best_val * 0 + rx + ry)):
                local_best = val
                local_tie = sd

        # Prefer progress even if no "steal" is possible.
        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    if best_move == (0, 0):
        # If boxed, move toward nearest resource while avoiding obstacles.
        nearest = min(resources, key=lambda r: dist_diag_manh(sx, sy, r[0], r[1]))
        tx, ty = nearest
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if (sx + dx, sy + dy) in obstacles:
            if (sx + dx, sy) not in obstacles:
                return [dx, 0]
            if (sx, sy + dy) not in obstacles:
                return [0, dy]
            return [0, 0]
        return [dx, dy]

    return [int(best_move[0]), int(best_move[1])]