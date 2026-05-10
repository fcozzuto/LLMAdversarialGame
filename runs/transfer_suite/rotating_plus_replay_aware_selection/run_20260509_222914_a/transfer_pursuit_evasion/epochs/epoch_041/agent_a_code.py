def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_list = observation.get("obstacles") or []
    obstacles = []
    for p in obs_list:
        if p and len(p) >= 2:
            obstacles.append((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role) or ("evasion" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obs_pen(x, y):
        if not obstacles:
            return 0.0
        dmin = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < dmin:
                dmin = d
        if dmin <= 0:
            return 1e6
        if dmin == 1:
            return 200.0
        if dmin == 2:
            return 60.0
        return 1.0 / (dmin + 1)

    best = None
    best_val = -10**18 if not is_evader else -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        pen = obs_pen(nx, ny)
        val = (-dist - pen) if not is_evader else (dist - pen)
        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]