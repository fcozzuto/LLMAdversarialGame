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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**18, 0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            # Pick the resource that we would target next (closest by Chebyshev distance),
            # then evaluate how well we can deny the opponent from reaching it.
            our_best_d = 10**9
            target = resources[0]
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < our_best_d:
                    our_best_d = d
                    target = (rx, ry)
            rx, ry = target
            opp_d = cheb(ox, oy, rx, ry)

            # Favor getting there first, and also prefer moving away from opponent when tied.
            # Small tie-break encourages progress and center pressure.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            score = (-3.5 * our_best_d) + (2.2 * opp_d) + 0.05 * cheb(nx, ny, sx, sy) + 0.001 * center
        else:
            # No visible resources: drift toward center while keeping away from opponent.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            opp_dist = cheb(nx, ny, ox, oy)
            score = 0.9 * opp_dist + 0.02 * center

        if score > best[0] + 1e-12:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]