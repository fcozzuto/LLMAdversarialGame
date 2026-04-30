def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0, -10**18)

    if not ok(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Favor moving onto a resource immediately, else move toward a resource where we have tempo vs opponent.
        score = 0
        if resources and (nx, ny) in obstacles:
            score -= 10**9

        if resources:
            immediate = 0
            for rx, ry in resources:
                if rx == nx and ry == ny:
                    immediate += 1
            if immediate:
                return [int(dx), int(dy)]

            best_res = -10**18
            for rx, ry in resources:
                our_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                # Advantage term: positive if we reach earlier (or equal).
                adv = opp_d - our_d
                # Prefer closer resources, but strongly prefer ones we can win.
                cand = adv * 100 - our_d
                # Tiny deterministic tie-break: prefer moving toward center and away from edges.
                center_bias = -abs((nx - (w - 1) / 2)) - abs((ny - (h - 1) / 2))
                cand += center_bias * 0.01
                if cand > best_res:
                    best_res = cand
            score += best_res

        # Obstacle/positioning: avoid being boxed by penalizing moves adjacent to obstacles.
        adj_obs = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if (tx, ty) in obstacles:
                    adj_obs += 1
        score -= adj_obs * 2

        if score > best[2]:
            best = (dx, dy, score)

    return [int(best[0]), int(best[1])]