def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    cx, cy = (W - 1) // 2, (H - 1) // 2

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Immediate greedy win if landing on resource
        if (nx, ny) in set(resources):
            return [dx, dy]

        if resources:
            # Choose move that maximizes our advantage over opponent for reachable resources
            my_best = 10**9
            opp_best = 10**9
            adv_best = -10**9
            tie_break = 10**9
            for rx, ry in resources:
                d_my = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)  # opponent position this turn
                adv = d_op - d_my  # positive means we are closer
                if adv > adv_best or (adv == adv_best and d_my < tie_break):
                    adv_best = adv
                    tie_break = d_my
                    my_best = d_my
                    opp_best = d_op
            # If both chase same resource, advantage should be positive; otherwise avoid pure chasing
            val = 50 * (adv_best) - 2 * my_best
            # Encourage not letting opponent get much closer to us
            opp_to_us = cheb(nx, ny, ox, oy)
            val += 1.5 * opp_to_us
            # Slight pull towards center to improve future options
            val -= 0.15 * cheb(nx, ny, cx, cy)
        else:
            # No resources: spread out from opponent and drift to center
            opp_to_us = cheb(nx, ny, ox, oy)
            val = 3.0 * opp_to_us - 0.15 * cheb(nx, ny, cx, cy)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move