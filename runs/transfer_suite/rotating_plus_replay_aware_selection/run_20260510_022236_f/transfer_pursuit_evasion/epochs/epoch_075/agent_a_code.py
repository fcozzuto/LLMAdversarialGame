def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "flee"))

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles or not inside(x, y)

    def mobility(x, y):
        m = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny):
                    m += 1
        return m

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        mob = mobility(nx, ny)
        # small tie-breakers deterministic
        center_bias = -abs((w - 1) / 2 - nx) - abs((h - 1) / 2 - ny)
        corner_bias = (nx in (0, w - 1) and ny in (0, h - 1)) - (nx in (0, w - 1) or ny in (0, h - 1))
        # Evader wants larger dist; pursuer wants smaller dist
        s = (dist if is_evader else -dist) + 0.7 * mob + 0.05 * center_bias + 0.02 * corner_bias
        if best_s is None or s > best_s:
            best_s = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]