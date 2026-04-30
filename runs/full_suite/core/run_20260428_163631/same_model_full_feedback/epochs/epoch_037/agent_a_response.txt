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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**9

    # Precompute opponent distance to each resource from current position (used for relative advantage).
    opp_dists = []
    for rx, ry in resources:
        opp_dists.append(cheb(ox, oy, rx, ry))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # If no resources, just maximize distance from opponent (stalling).
        if not resources:
            val = cheb(nx, ny, ox, oy)
        else:
            # Evaluate relative advantage to the best resource (where we are closer sooner).
            # Score blends: (opp_dist - our_dist) to race resources, then small penalty for our absolute distance.
            best_adv = -10**9
            best_our = 10**9
            for i, (rx, ry) in enumerate(resources):
                our = cheb(nx, ny, rx, ry)
                opp = opp_dists[i]
                adv = opp - our
                if adv > best_adv:
                    best_adv = adv
                if our < best_our:
                    best_our = our
            # Also incorporate opponent avoidance to reduce their ability to contest nearby resources.
            opp_now = cheb(nx, ny, ox, oy)
            val = (best_adv * 10) + (opp_now * 0.5) - (best_our * 0.2)

        # Deterministic tie-break: prefer smaller |dx|+|dy|, then lexicographically.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            cur = best_move
            if (abs(dx) + abs(dy), dx, dy) < (abs(cur[0]) + abs(cur[1]), cur[0], cur[1]):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]