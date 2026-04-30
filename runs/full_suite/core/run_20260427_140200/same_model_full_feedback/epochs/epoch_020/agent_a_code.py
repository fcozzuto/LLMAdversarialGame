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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs.sort()

    # Stronger response: avoid letting opponent be closer to any resource than we are.
    bestm = (0, 0)
    bestv = -10**18
    danger_now = cheb(sx, sy, ox, oy) <= 1

    def opp_dist_to_resource(px, py, rx, ry):
        return cheb(px, py, rx, ry)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Safety: if we can capture nearby, be bolder; otherwise avoid adjacency.
        danger_after = cheb(nx, ny, ox, oy) <= 1
        safety = 0
        if danger_now and not danger_after:
            safety += 5
        if (not danger_now) and danger_after:
            safety -= 6
        if danger_after:
            safety -= 2

        # Terminal-ish benefit: capture if standing on a resource.
        cap = 1 if (nx, ny) in obstacles else 0
        if resources and any((nx, ny) == r for r in resources):
            safety += 100

        # Target choice: maximize (our_advantage) where advantage = opp_dist - our_dist.
        adv_best = -10**18
        res_closest = 10**9
        for rx, ry in resources:
            d0 = cheb(nx, ny, rx, ry)
            d1 = opp_dist_to_resource(ox, oy, rx, ry)
            adv = d1 - d0
            if adv > adv_best:
                adv_best = adv
            if d0 < res_closest:
                res_closest = d0

        # If no resources known, drift to increase separation while staying safe.
        if not resources:
            sep = cheb(nx, ny, ox, oy)
            v = sep + safety
        else:
            # Bonus for being closer to some resource and for denying opponent (advantage).
            v = (adv_best * 8) + (-res_closest * 2) + safety
            # Mild bias: prefer moves that progress toward opponent's side only when advantageous.
            progress = cheb(ox, oy, nx, ny)  # smaller means closer to opponent
            v += (-progress if adv_best > 0 else progress) * 0.5

        # Deterministic tie-break: lexicographic on move after rounding.
        if v > bestv:
            bestv = v
            bestm = (dx, dy)
        elif v == bestv and (dx, dy) < bestm:
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]