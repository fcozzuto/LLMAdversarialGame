def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opponent_role and "pursuer" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def edge_pen(x, y):
        d = min(x, w - 1 - x, y, h - 1 - y)
        return -float(d)  # closer to edges => worse

    best = (0, 0)
    bestv = -10**18 if is_evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if nx == ox and ny == oy:
            if is_evader:
                continue
            return [dx, dy]  # immediate capture
        d = dist2(nx, ny)
        center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        stay_pen = 0.15 if dx == 0 and dy == 0 else 0.0

        if is_evader:
            v = d + 0.03 * center + 0.08 * edge_pen(nx, ny) - stay_pen
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        else:
            v = -d + 0.02 * (-center) + 0.06 * (-edge_pen(nx, ny)) - stay_pen
            if v < bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)

    return [int(best[0]), int(best[1])]