def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    rpos = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                rpos.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if (sx, sy) in obs:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [int(dx), int(dy)]
        return [0, 0]

    # Candidate evaluation: maximize (opp predicted advantage - self disadvantage)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = [0, 0]
    best_val = -10**30

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ns = cheb((nx, ny), (nx, ny))  # 0, but keep deterministic structure
        if rpos:
            self_near = 10**9
            self_center = abs(nx - cx) + abs(ny - cy)
            for r in rpos:
                d = cheb((nx, ny), r)
                if d < self_near: self_near = d
            # Opponent can move once; predict their best-case nearest-resource distance
            opp_best = 10**9
            for odx, ody in dirs:
                onx, ony = ox + odx, oy + ody
                if not inb(onx, ony) or (onx, ony) in obs:
                    continue
                opp_near = 10**9
                for r in rpos:
                    d = cheb((onx, ony), r)
                    if d < opp_near: opp_near = d
                if opp_near < opp_best: opp_best = opp_near
            # Lower self_near and higher opp_best is better; center tie-break helps escape stalemates
            val = (opp_best - self_near) * 1000 - self_center * 0.5 - ns
        else:
            # No resources: move toward center while staying safe
            self_center = abs(nx - cx) + abs(ny - cy)
            val = -self_center
        if val > best_val:
            best_val = val
            best = [int(dx), int(dy)]

    return [int(best[0]), int(best[1])]