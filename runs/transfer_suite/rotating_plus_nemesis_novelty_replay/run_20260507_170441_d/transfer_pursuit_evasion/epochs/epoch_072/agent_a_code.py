def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    role = (observation.get("self_role", "") or "").lower()
    evader = ("evader" in role) or ("runner" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_val = -10**18 if evader else 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        if res:
            d = min(man(nx, ny, rx, ry) for rx, ry in res)
            # Prefer moves that get closer to resources (or, if evading, still bias away from opponent).
            if evader:
                val = d - 2 * man(nx, ny, ox, oy)
                if val > best_val:
                    best_val, best = val, [dx, dy]
            else:
                val = d + 2 * man(nx, ny, ox, oy)
                if val < best_val:
                    best_val, best = val, [dx, dy]
        else:
            d_op = man(nx, ny, ox, oy)
            val = d_op if evader else d_op
            if evader:
                if val > best_val:
                    best_val, best = val, [dx, dy]
            else:
                if val < best_val:
                    best_val, best = val, [dx, dy]

    if best is not None:
        return best
    # Fallback: stay if possible
    if free(sx, sy):
        return [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            return [dx, dy]
    return [0, 0]