def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def get_xy(v, default=None):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default

    sp = get_xy(observation.get("self_position", None), (0, 0))
    op = get_xy(observation.get("opponent_position", None), sp)
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]

    obs = set()
    for o in observation.get("obstacles", []) or []:
        p = get_xy(o, None) if o is not None else None
        if p is None:
            continue
        x, y = p
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in observation.get("resources", []) or []:
        p = get_xy(r, None) if r is not None else None
        if p is None:
            continue
        x, y = p
        if free(x, y):
            resources.append((x, y))

    if not resources:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if (sx, sy) in resources:
        # Even if we are on a resource, prefer not to leave unless it improves contest.
        pass

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        our_best_gain = -10**9
        # Choose the resource that makes this move most favorable versus opponent.
        for tx, ty in resources:
            self_d = abs(tx - nx) + abs(ty - ny)
            opp_d = abs(tx - ox) + abs(ty - oy)
            # Higher is better: we want to be closer than opponent.
            contest = (opp_d - self_d)
            # Mild preference for picking up sooner (smaller self_d).
            val = contest * 10 - self_d
            # Deterministic tie: also bias toward moving closer in x then y.
            xbias = -abs(tx - nx) - abs(ty - ny) * 0.01
            score = val + xbias
            if score > our_best_gain:
                our_best_gain = score
        if best is None or our_best_gain > best[0]:
            best = (our_best_gain, dx, dy)
        elif our_best_gain == best[0]:
            # Deterministic tie-break ordering
            if (dx, dy) < (best[1], best[2]):
                best = (our_best_gain, dx, dy)

    return [best[1], best[2]]