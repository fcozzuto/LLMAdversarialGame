def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_score = -10**18

    # If possible, chase the resource that gives best "advantage" (closer than opponent).
    if resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not cell_ok(nx, ny):
                continue
            score = 0
            # Prefer states that are closer to some resource and farther from that resource for opponent.
            local_best = -10**18
            for rx, ry in resources:
                our_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                # Big reward for being closer than opponent; small penalty for distance.
                adv = opp_d - our_d
                val = adv * 1000 - our_d
                if val > local_best:
                    local_best = val
            # Prefer not to waste a step if staying is worse than moving.
            score = local_best
            # Tiny tie-break: move toward center a bit (deterministic).
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score -= 0.001 * cheb(int(nx), int(ny), int(cx), int(cy))
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # No visible resources: move away from opponent and avoid obstacles.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not cell_ok(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            score = d * 10 - cheb(int(nx), int(ny), (w - 1)//2, (h - 1)//2)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]