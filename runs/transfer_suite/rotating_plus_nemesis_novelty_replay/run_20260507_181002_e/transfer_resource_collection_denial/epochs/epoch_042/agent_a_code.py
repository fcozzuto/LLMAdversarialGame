def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def p2(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            q = v.get("position", v.get("pos", None))
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return int(q[0]), int(q[1])
        return None

    sp = p2(observation.get("self_position", None)) or (0, 0)
    op = p2(observation.get("opponent_position", None)) or (w - 1, h - 1)
    sx, sy = sp
    ox, oy = op

    obs = set()
    for o in observation.get("obstacles", []) or []:
        q = p2(o)
        if q:
            x, y = q
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in observation.get("resources", []) or []:
        q = p2(r)
        if q:
            x, y = q
            if free(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = ox, oy
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if (d, 0, dx, dy) < best:
                best = (d, 0, dx, dy)
        _, _, dx, dy = best
        return [dx, dy]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = (10**18, 10**18, 0, 0)  # (score, self_dist, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Tie-break target: maximize (opp closer? worse) => minimize (self_adv - opp_adv)
        # Score formulation favors cells that we reach much earlier than opponent, but also progresses.
        local_best = 10**18
        for rx, ry in resources:
            self_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            # higher opp_d is good; we want our_d small and opp_d large
            # also slightly prefer smaller self_d to move efficiently.
            val = (self_d - 0.9 * opp_d) + 0.05 * self_d
            if val < local_best:
                local_best = val
        # Secondary: prefer staying aligned with the resource that minimizes our distance overall
        self_to_closest = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        cand = (local_best, self_to_closest, dx, dy)
        if cand < best:
            best = cand

    _, _, dx, dy = best
    return [dx, dy]