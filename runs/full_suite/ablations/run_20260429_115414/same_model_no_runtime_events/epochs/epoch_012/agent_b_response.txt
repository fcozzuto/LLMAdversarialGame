def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestv = -10**18
    best = (0, 0)

    # Precompute nearest few resources for deterministic scoring
    res_sorted = sorted(res, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))
    center = (w // 2, h // 2)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        d_opp = cheb(nx, ny, ox, oy)
        d_center = cheb(nx, ny, center[0], center[1])

        v = 0.0
        # Strongly avoid being adjacent to opponent (unless it also targets a very near resource)
        if d_opp <= 1:
            v -= 20.0
        else:
            v += 0.8 * d_opp

        if res_sorted:
            # Go after the closest resource; if opponent can reach it sooner, contest only if close enough.
            r1 = res_sorted[0]
            my_d = cheb(nx, ny, r1[0], r1[1])
            op_d = cheb(ox, oy, r1[0], r1[1])
            v += 12.0 / (1 + my_d)

            if op_d < my_d:
                # Contest: still prefer reducing my distance, but penalize if hopelessly behind
                v -= 3.0 * (my_d - op_d)
            # Secondary resource shaping for stability
            if len(res_sorted) > 1:
                r2 = res_sorted[1]
                v += 2.0 / (1 + cheb(nx, ny, r2[0], r2[1]))

        else:
            # If no visible resources, drift toward center while keeping distance from opponent
            v += 0.3 * (w + h - d_center)

        # Deterministic tie-break
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]