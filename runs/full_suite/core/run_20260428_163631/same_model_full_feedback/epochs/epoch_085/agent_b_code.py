def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    obstacles.discard((sx, sy))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target_score(cx, cy):
        if not resources:
            return -10**9, None
        best = -10**18
        best_res = None
        for rx, ry in resources:
            d_me = cheb(cx, cy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources we are not behind for; otherwise discount
            behind = d_me - d_op
            if behind <= 0:
                base = 6 - d_me
            else:
                base = -2 - d_me - 2 * behind
            # Small center-ish bias to reduce wandering
            center_bias = -(abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)) * 0.02
            # Extra incentive if landing directly on a resource
            collect_bonus = 100 if (cx == rx and cy == ry) else 0
            val = base + center_bias + collect_bonus
            if val > best:
                best = val
                best_res = (rx, ry)
        return best, best_res

    best_move = (0, 0)
    best_val = -10**18

    # Strategic change: evaluate move by contesting resources against opponent, not only chasing nearest.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        target_val, _ = best_target_score(nx, ny)
        # Opponent pressure: slightly prefer staying farther when resource contest is similar
        dop = cheb(nx, ny, ox, oy)
        opp_pen = -0.06 * max(0, 3 - dop)  # only penalize when close
        val = target_val + opp_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]