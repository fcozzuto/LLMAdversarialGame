def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    srole = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in srole) or ("catch" in srole) or ("seeker" in srole) or ("chase" in srole)

    obs = observation.get("obstacles", []) or []
    oset = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist_goal(x, y):
        if is_pursuer:
            return max(abs(x - ox), abs(y - oy))
        c = max(corners, key=lambda t: abs(t[0] - ox) + abs(t[1] - oy))
        return - (abs(x - c[0]) + abs(y - c[1]))

    best = None
    if is_pursuer:
        best_val = 10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in oset:
                continue
            val = dist_goal(nx, ny)
            if val < best_val or (val == best_val and (dx, dy) < best):
                best_val = val
                best = (dx, dy)
    else:
        best_val = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in oset:
                continue
            val = dist_goal(nx, ny)
            if val > best_val or (val == best_val and (best is None or (dx, dy) < best)):
                best_val = val
                best = (dx, dy)

    if best is not None:
        return [int(best[0]), int(best[1])]

    safe = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in oset:
            safe.append((dx, dy))
    if safe:
        safe.sort()
        return [int(safe[0][0]), int(safe[0][1])]
    return [0, 0]