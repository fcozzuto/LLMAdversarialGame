def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    bestv = -10**18

    # Prefer reducing distance to resources that opponent is less likely to reach first.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy

        # Deterministic tie-break: prefer moving along increasing y early, then along increasing x.
        dir_bonus = (ny - sy) * 0.05 + (nx - sx) * 0.01
        # Also avoid getting too close to opponent unless it secures a resource.
        opp_close_pen = -1.0 / (1 + cheb(nx, ny, ox, oy))

        best_candidate = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Advantage if we can arrive sooner; slight preference for nearer resources.
            cand = (od - sd) * 2.0 - sd * 0.3 + (rx * 0.001 + ry * 0.001)
            if cand > best_candidate:
                best_candidate = cand
        v = best_candidate + dir_bonus + opp_close_pen

        if v > bestv:
            bestv = v
            best = [dx, dy]
        elif v == bestv and best is not None:
            # Deterministic tie-break among equal values: prefer not staying, then prefer (0,1), then lexicographic.
            if best != [dx, dy]:
                stay_best = (best[0] == 0 and best[1] == 0)
                stay_new = (dx == 0 and dy == 0)
                if stay_best and not stay_new:
                    best = [dx, dy]
                elif not stay_best and stay_new:
                    pass
                else:
                    if (best[0], best[1]) > (dx, dy):
                        best = [dx, dy]
    return best if best is not None else [0, 0]