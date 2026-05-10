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
        mode = "pursue" if (("evad" in opponent_role) or (opponent_role == "evader")) else "evade"

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    if mode == "pursue":
        best_val = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            val = -d2(nx, ny, ox, oy)
            val += 0.02 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * -1  # slight center bias
            if (dx, dy) == (0, 0):
                val -= 0.001
            if val > best_val:
                best_val = val
                best = (dx, dy)
    else:
        best_val = -10**18
        # Evader: maximize distance from pursuer, but prefer moves that keep near a "goal corner"
        corner = (0, 0) if (ox + oy) > (w - 1 - ox + h - 1 - oy) else (w - 1, h - 1)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            val = d2(nx, ny, ox, oy)
            val += 0.001 * d2(nx, ny, corner[0], corner[1])  # encourage cornering
            if (dx, dy) == (0, 0):
                val -= 0.001
            if val > best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]