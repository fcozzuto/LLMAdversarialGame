def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    if ("evad" in self_role) or self_role == "evader":
        mode = "evade"
    elif ("purs" in self_role) or self_role == "pursuer":
        mode = "pursue"
    else:
        mode = "pursue" if ("evad" in opponent_role) or opponent_role == "evader" else "evade"

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(x, y):
        # penalty for being adjacent to obstacles (keeps mobility around wall runners)
        adj = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (x + dx, y + dy) in obs:
                adj += 1
        if mode == "pursue":
            # minimize distance; slight preference to move toward "center" to avoid being kited along walls
            d2 = (x - ox) * (x - ox) + (y - oy) * (y - oy)
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            return d2 * 10.0 + center + adj * 5.0
        else:
            # maximize distance; prefer corners and avoid getting boxed in by obstacles
            d2 = (x - ox) * (x - ox) + (y - oy) * (y - oy)
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            # choose corners by preferring farthest from center when evading
            return -(d2 * 10.0 + center * 2.0 - adj * 3.0)

    best_dx, best_dy = 0, 0
    if mode == "pursue":
        best_val = 10**30
    else:
        best_val = -10**30

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        v = score_cell(nx, ny)
        if mode == "pursue":
            if v < best_val - 1e-9 or (abs(v - best_val) <= 1e-9 and (dx, dy) < (best_dx, best_dy)):
                best_val, best_dx, best_dy = v, dx, dy
        else:
            if v > best_val + 1e-9 or (abs(v - best_val) <= 1e-9 and (dx, dy) < (best_dx, best_dy)):
                best_val, best_dx, best_dy = v, dx, dy

    return [int(best_dx), int(best_dy)]