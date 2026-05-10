def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(0, 0)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx != 0 or dy != 0:
                if inb(sx + dx, sy + dy):
                    moves.append((dx, dy))

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def best_target_score(px, py):
        best = (-10**18, 10**9)
        for rx, ry in res:
            sd = cheb((px, py), (rx, ry))
            od = cheb((ox, oy), (rx, ry))
            # Prefer resources where we are closer than opponent; otherwise reduce their advantage.
            primary = (od - sd) * 100 - sd
            if primary > best[0] or (primary == best[0] and sd < best[1]):
                best = (primary, sd)
        return best[0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        px, py = sx + dx, sy + dy
        v = best_target_score(px, py)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]