def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_move_center():
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**9, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                val = -md(nx, ny, cx, cy) - 0.1 * md(nx, ny, ox, oy)
                if val > best[0]:
                    best = (val, (dx, dy))
        return list(best[1])

    if not resources:
        return best_move_center()

    best_val = -10**18
    best = (0, 0)
    center_bias = (w - 1) // 2, (h - 1) // 2
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Advantage heuristic: how much closer we become vs opponent for the best reachable resource.
        adv_best = -10**18
        near_best = 10**9
        for rx, ry in resources:
            opp_d = md(ox, oy, rx, ry)
            self_d = md(nx, ny, rx, ry)
            adv = opp_d - self_d
            if adv > adv_best:
                adv_best = adv
                near_best = self_d
            elif adv == adv_best and self_d < near_best:
                near_best = self_d

        # Mild center preference to avoid edge patrol traps when advantages tie.
        cbx, cby = center_bias
        val = adv_best - 0.01 * near_best - 0.001 * md(nx, ny, cbx, cby) - 0.0005 * md(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]