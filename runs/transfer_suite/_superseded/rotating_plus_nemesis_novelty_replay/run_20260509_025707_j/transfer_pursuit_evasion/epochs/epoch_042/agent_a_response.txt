def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("runner" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    ti = int(observation.get("turn_index", 0) or 0)
    parity = ti & 1

    def manhattan(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def clearance(x, y):
        if not obstacles:
            return 10**6
        best = 10**6
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_now = manhattan(sx, sy, ox, oy)
        d_new = manhattan(nx, ny, ox, oy)
        dc = clearance(nx, ny)

        # Tie-break deterministically by parity-weighted direction ordering
        dir_bias = (dx * 3 + dy * 5 + parity) * 1e-3

        if evader:
            # Maximize distance; avoid getting too close to obstacles.
            val = (d_new - d_now) * 10.0 + dc * 0.25 + dir_bias
        else:
            # Minimize distance; avoid tight obstacle proximity (can help pursuit stability).
            val = (d_now - d_new) * 10.0 + dc * 0.08 + dir_bias

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]