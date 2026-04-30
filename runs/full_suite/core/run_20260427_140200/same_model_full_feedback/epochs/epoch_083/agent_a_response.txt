def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neighbor_obstacle_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    pen += 1
        return pen

    # Strategy change: secure "contested" resources by maximizing advantage, but when none, run to deny by moving toward opponent-closest.
    best_move = (0, 0)
    best_val = -10**9

    if resources:
        # Deterministic tie-break by resource position.
        resources = sorted(resources)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            our_to_opp = cheb(nx, ny, ox, oy)
            step_pen = neighbor_obstacle_pen(nx, ny)
            best_target = -10**9
            for rx, ry in resources:
                du = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Advantage: we want du < do. If losing, still pick an opponent-close target to contest.
                adv = (do - du)
                # Side bias: prefer resources closer to our side relative to opponent position.
                side = (rx - ox) * (rx - sx)
                # If we are already ahead, favor speed; else favor contest.
                speed_bias = 2 if adv >= 0 else -1
                val = speed_bias * (-du) + (2 * adv) + (0.1 * side) - step_pen
                if val > best_target:
                    best_target = val
            # Also add light anti-chase: if we can't get advantage, keep distance from opponent.
            val_total = best_target + (0.05 * our_to_opp)
            if val_total > best_val:
                best_val = val_total
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]