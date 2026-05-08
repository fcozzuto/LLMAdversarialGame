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

    def clamp(x, y):
        if x < 0:
            x = 0
        elif x >= w:
            x = w - 1
        if y < 0:
            y = 0
        elif y >= h:
            y = h - 1
        return x, y

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def edge_margin(x, y):
        # prefer staying away from edges for evasion to reduce corner lock-in
        return min(x, y, w - 1 - x, h - 1 - y)

    best_move = moves[0]
    best_val = None

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obs:
            continue
        d = dist2(nx, ny)
        if i_am_evader:
            val = (d, edge_margin(nx, ny), -abs(nx - sx) - abs(ny - sy))
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]
        else:
            # pursuer: greedily minimize distance to opponent
            val = (-d, -edge_margin(nx, ny), abs(nx - sx) + abs(ny - sy))
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]