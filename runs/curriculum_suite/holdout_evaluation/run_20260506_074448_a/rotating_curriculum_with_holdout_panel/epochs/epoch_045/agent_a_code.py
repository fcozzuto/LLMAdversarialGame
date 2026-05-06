def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    # Determine which resources opponent is currently closer to (i.e., we should contest).
    opp_closer = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        oppd = man(ox, oy, rx, ry)
        myd = man(sx, sy, rx, ry)
        if oppd < myd:
            opp_closer.append((oppd, rx, ry))
    opp_closer.sort()  # closest to opponent first

    # Small deterministic "center" tie-breaker to avoid oscillation.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_dx, best_dy = 0, 0
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Avoid stepping adjacent to an obstacle if it doesn't help (mild penalty).
        adj_obs = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                    adj_obs += 1

        # Main objective: contest resources where opponent is ahead, otherwise take the best reachable.
        val = 0.0
        if opp_closer:
            # Focus on top few contested resources.
            for i in range(min(4, len(opp_closer))):
                _, rx, ry = opp_closer[i]
                oppd = man(nx, ny, ox, oy)
                myd = man(nx, ny, rx, ry)
                opp_to_res = man(ox, oy, rx, ry)
                # Positive if we move to improve our relative position on that resource.
                contest = (opp_to_res - myd)
                # Prefer moves that also keep us relatively close to opponent (intercept/steal).
                val += 3.0 * contest + 0.25 * (man(nx, ny, ox, oy) - oppd) - 0.1 * myd
                # Slightly prefer reducing distance to the contested resource itself.
                val += -0.02 * man(nx, ny, rx, ry)
        else:
            # No contested resources: greedily move toward the best next resource vs opponent timing.
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                myd = man(nx, ny, rx, ry)
                oppd = man(ox, oy, rx, ry)
                # Prefer resources where we are not too far behind opponent.
                val += 2.5 * (oppd - myd) - 0.06 * myd

        # Mild center tie-breaker and obstacle adjacency penalty.
        cd = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        val += -0.003 * cd - 0.08 * adj_obs

        # Deterministic tie-break: prefer smaller |dx|+|dy| then lexicographic by dx,dy.
        key = (-(abs(dx) + abs(dy)), dx, dy)
        best_key = (-(abs(best_dx) + abs(best_dy)), best_dx, best_dy)
        if val > best_val + 1e-12 or (abs(val - best_val) <= 1e-12 and key >= best_key):
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]