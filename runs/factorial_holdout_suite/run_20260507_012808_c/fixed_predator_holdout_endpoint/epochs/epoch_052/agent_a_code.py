def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = (None, -10**9, 10**9)

    # Precompute nearest resource distances to current positions for scale
    cur_self = min(cheb(sx, sy, rx, ry) for rx, ry in resources)
    cur_opp = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
    scale = max(1, cur_opp + cur_self)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate by best-target advantage; also add slight preference for moving closer to the overall best resource.
        best_adv = -10**9
        best_self_dist = 10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent
            # Penalize if we are far from any resource (to avoid wandering)
            adv -= (sd > 0) * (sd / scale) * 0.5
            if adv > best_adv or (adv == best_adv and sd < best_self_dist):
                best_adv = adv
                best_self_dist = sd

        # Directly compute "resource-at-current" bonus if stepping onto a resource
        on_res_bonus = 2.0 if (nx, ny) in set(resources) else 0.0

        # Mild tie-break to reduce opponent contesting by preferring targets closer to us now
        value = best_adv + on_res_bonus - (best_self_dist / scale) * 0.2

        # Deterministic tie-break: prefer smaller |dx|+|dy|, then lexical move order already stable by list.
        dist_cost = abs(dx) + abs(dy)
        if value > best[1] or (value == best[1] and dist_cost < best[2]):
            best = ((dx, dy), value, dist_cost)

    dx, dy = best[0]
    return [int(dx), int(dy)]