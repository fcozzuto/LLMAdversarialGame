def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    opp_d_cache = {}
    best_target = resources[0]
    best_t_score = -10**18
    best_self_d = 10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        tscore = (od - sd) * 1000 - sd  # favor resources where we have advantage
        if (tscore > best_t_score) or (tscore == best_t_score and sd < best_self_d):
            best_t_score = tscore
            best_self_d = sd
            best_target = (rx, ry)

    tx, ty = best_target
    opp_d = cheb(ox, oy, tx, ty)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        our_d = cheb(nx, ny, tx, ty)
        # Prefer decreasing our distance; also avoid stepping into worse long-term positions.
        val = (opp_d - our_d) * 1000 - our_d
        # Add small deterministic tie-break: keep closer to center if tied.
        if val == best_val:
            cx, cy = w / 2 - 0.5, h / 2 - 0.5
            dist_cur = abs(nx - cx) + abs(ny - cy)
            dist_best = abs(best_move[0] + sx - cx) + abs(best_move[1] + sy - cy)
            if dist_cur < dist_best:
                best_move = (dx, dy)
        elif val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]