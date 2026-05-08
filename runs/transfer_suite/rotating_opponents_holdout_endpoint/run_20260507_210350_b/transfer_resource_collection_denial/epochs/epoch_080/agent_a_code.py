def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = (None, -10**9)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        # score: prefer moves that reduce our distance to a resource
        # and where we are (relatively) closer than opponent (resource_denier).
        val = 0
        for rx, ry in resources:
            d1 = md(nx, ny, rx, ry)
            d0 = md(sx, sy, rx, ry)
            if d1 < d0:
                val += 4
            if d1 == 0:
                val += 1000
            # if opponent can get there much faster, deprioritize
            od1 = md(ox, oy, rx, ry)
            diff = od1 - d1  # positive means we are closer
            val += 3 * diff
            val += -2 * d1
        # tie-break: prefer staying less if equal
        if val > best[1] or (val == best[1] and dx == 0 and dy == 0):
            best = ((dx, dy), val)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]