def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    roles = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    self_is_evader = ("evader" in roles) and ("purs" not in roles)

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        d = dist2(nx, ny, ox, oy)
        if self_is_evader:
            corner_bonus = max(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
            key = (d, corner_bonus, -abs(nx - sx) - abs(ny - sy))
            cmp = 1
        else:
            corner_bias = -min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
            key = (-d, corner_bias, -abs(nx - sx) - abs(ny - sy))
            cmp = -1

        if best is None:
            best = (key, (dx, dy))
        else:
            if cmp == 1:
                if key > best[0] or (key == best[0] and (dx, dy) < best[1]):
                    best = (key, (dx, dy))
            else:
                if key > best[0] or (key == best[0] and (dx, dy) < best[1]):
                    best = (key, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]