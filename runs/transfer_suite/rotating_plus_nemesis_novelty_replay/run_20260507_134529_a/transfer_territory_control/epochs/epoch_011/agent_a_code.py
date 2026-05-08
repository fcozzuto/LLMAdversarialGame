def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def cells(key):
        out = []
        pts = observation.get(key) or []
        for p in pts:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.append((x, y))
        return out

    obs_list = cells("obstacles")
    obs = set(obs_list)
    unclaimed = cells("unclaimed_cells") + cells("resources")
    if not unclaimed:
        unclaimed = cells("resources")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if unclaimed:
        target = min(unclaimed, key=lambda p: dist((sx, sy), p))
    else:
        target = (ox, oy)
        if w > 1 and h > 1:
            target = (max(0, min(w - 1, sx + 1)), max(0, min(h - 1, sy + 1)))

    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_t = dist((nx, ny), target)
        d_o = dist((nx, ny), (ox, oy))
        val = (-4 * d_t) + (2 * d_o) + (1 if (nx, ny) in unclaimed else 0)
        if dx == 0 and dy == 0:
            val -= 0.5
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]