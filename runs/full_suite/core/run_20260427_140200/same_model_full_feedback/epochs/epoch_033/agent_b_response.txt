def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    obs_pen_cache = {}
    def near_obs_pen(x, y):
        k = (x, y)
        if k in obs_pen_cache:
            return obs_pen_cache[k]
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    pen += 2
        obs_pen_cache[k] = pen
        return pen

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_score = -10**18
    best_move = [0, 0]
    rem = int(observation.get("remaining_resource_count") or len(resources))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        me = (nx, ny)

        opp_d = cheb(me, (ox, oy))
        # Prefer being farther from opponent to reduce contention.
        base = opp_d * 0.8 - near_obs_pen(nx, ny) * 1.2

        if not resources:
            score = base
        else:
            score = base
            # Choose best contested objective: high (op_d - my_d) and low my_d.
            local_best = -10**18
            for r in resources:
                myd = cheb(me, r)
                opd = cheb((ox, oy), r)
                # Positive means we can reach sooner or tie.
                contested = (opd - myd)
                # Slightly prefer closer targets to finish collection.
                val = contested * 3.0 - myd * (0.35 + 0.15 * (rem > 6))
                # If we step onto a resource, strongly prefer it.
                if myd == 0:
                    val += 40
                # Also nudge away from allowing immediate opponent pick.
                if opd == 1:
                    val -= 2.5
                if val > local_best:
                    local_best = val
            score += local_best
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]