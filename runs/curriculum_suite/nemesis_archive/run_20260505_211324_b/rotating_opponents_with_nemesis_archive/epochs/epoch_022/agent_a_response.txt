def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int):
                if 0 <= x < w and 0 <= y < h:
                    obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and (x, y) not in obs:
                if 0 <= x < w and 0 <= y < h:
                    res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best = None
    best_val = -10**18

    # Evaluate moves by maximizing expected advantage: (opponent distance - my distance) to best target,
    # with a slight tie-break toward reducing my distance.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy  # engine keeps in place; mirror that deterministically

        myd_min = 10**9
        adv_best = -10**9
        for rx, ry in res:
            d_me = md(nx, ny, rx, ry)
            d_op = md(ox, oy, rx, ry)
            if d_me < myd_min:
                myd_min = d_me
            adv = d_op - d_me  # positive means I can reach sooner (or same turn)
            if adv > adv_best:
                adv_best = adv

        # Encourage taking close wins; discourage drifting when no advantage.
        val = adv_best * 1000 - myd_min
        if val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: prefer staying less, then smaller |dx|+|dy|, then dx,dy.
            cur = best
            if cur is None:
                best = (dx, dy)
            else:
                if (dx, dy) == (0, 0) and cur != (0, 0):
                    continue
                if (abs(dx) + abs(dy), dx, dy) < (abs(cur[0]) + abs(cur[1]), cur[0], cur[1]):
                    best = (dx, dy)

    return [int(best[0]), int(best[1])]