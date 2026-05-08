def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def to_xy(obj):
        if isinstance(obj, (list, tuple)) and len(obj) == 2:
            return int(obj[0]), int(obj[1])
        if isinstance(obj, dict):
            q = obj.get("position", obj.get("pos", None))
            if isinstance(q, (list, tuple)) and len(q) == 2:
                return int(q[0]), int(q[1])
        return None

    res = []
    for r in resources:
        t = to_xy(r)
        if t is not None:
            res.append(t)
    obs = set()
    for o in obstacles:
        t = to_xy(o)
        if t is not None:
            obs.add(t)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not dirs:
        return [0, 0]

    if not res:
        # fallback: drift toward opponent's corner opposite ours (heuristic for resource density)
        tx, ty = (w - 1, 0) if (sx == 0 and sy == h - 1) else (0, h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def cheb(a, b, c, d):
        ax = abs(a - c)
        ay = abs(b - d)
        return ax if ax > ay else ay

    # One-step evaluation: prefer immediate capture, then best chance to be first
    best_move = (0, 0)
    best_score = None

    for mx, my in dirs:
        nx, ny = sx + mx, sy + my
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue

        immediate = 1 if (nx, ny) in set(res) else 0

        # compute best "advantage" resource for us from next position
        our_best = None
        opp_best = None
        for rx, ry in res:
            # Chebyshev distance approximates diagonal reach well
            d_ours = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_ours  # positive means we get there first
            if our_best is None or (adv > our_best[0]) or (adv == our_best[0] and d_ours < our_best[1]):
                our_best = (adv, d_ours, rx, ry)
            if opp_best is None or (d_opp < opp_best[0]):
                opp_best = (d_opp, rx, ry)

        adv, d_ours, rx, ry = our_best
        # tie-breakers: maximize advantage, then minimize our distance, then prefer moves that reduce opponent options
        opp_closest = opp_best[0]
        score = (immediate, adv, -d_ours, -(max(0, opp_closest - cheb(nx, ny, rx, ry))), -(abs(rx - (w - 1)) + abs(ry - (h - 1))), (mx, my))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]