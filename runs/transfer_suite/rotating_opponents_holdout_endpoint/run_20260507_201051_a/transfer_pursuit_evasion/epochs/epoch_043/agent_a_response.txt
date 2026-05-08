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
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))  # farthest corner from opponent

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def adj_obstacle_count(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if not inb(nx, ny) or (nx, ny) in obs:
                    c += 1
        return c

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            score = -10**9 if not i_am_evader else -10**9
        else:
            d_op = dist2(nx, ny, ox, oy)
            d_op_cur = dist2(sx, sy, ox, oy)
            d_tar = abs(nx - tx) + abs(ny - ty)
            d_tar_cur = abs(sx - tx) + abs(sy - ty)
            risk = adj_obstacle_count(nx, ny)
            if i_am_evader:
                score = 3.0 * d_op + 0.5 * (d_tar - d_tar_cur) - 0.3 * risk + 0.1 * (d_op - d_op_cur)
            else:
                score = -2.6 * d_op - 0.1 * (d_tar - d_tar_cur) - 0.25 * risk - 0.05 * (d_op - d_op_cur)
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best