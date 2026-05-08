def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    i_am_evader = ("evader" in self_role) or ("pursuer" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    def obstacle_risk(x, y):
        if (x, y) in obs:
            return 10**9
        risk = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if not inb(nx, ny) or (nx, ny) in obs:
                    risk += 1
        return risk

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = dist2(nx, ny, ox, oy)
        risk = obstacle_risk(nx, ny)
        border = (1 if nx == 0 else 0) + (1 if nx == w - 1 else 0) + (1 if ny == 0 else 0) + (1 if ny == h - 1 else 0)

        if i_am_evader:
            # maximize survival: stay far, avoid borders/obstacles
            val = d - 0.9 * risk - 0.25 * border
        else:
            # chase: minimize distance; avoid obstacles/borders that slow pursuit
            val = -d - 0.7 * risk - 0.15 * border

        if best is None or (val > best_val) or (val == best_val and (dx, dy) < best):
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]