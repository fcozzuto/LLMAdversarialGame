def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) == 2:
                return int(p[0]), int(p[1])
        return None

    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = to_xy(observation.get("self_position", [0, 0])) or (0, 0)
    ox, oy = to_xy(observation.get("opponent_position", [0, 0])) or (w - 1, h - 1)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        t = to_xy(o)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        t = to_xy(r)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                val = -(abs(nx - ox) + abs(ny - oy))  # drift away from opponent
                if val > best[2] or (val == best[2] and (dx, dy) < (best[0], best[1])):
                    best = (dx, dy, val)
        return [best[0], best[1]]

    def min_dists(px, py):
        md = 10**9
        second = 10**9
        for x, y in res:
            d = abs(x - px) + abs(y - py)
            if d < md:
                second = md
                md = d
            elif d < second:
                second = d
        return md, second

    # Race objective: maximize (opponent nearest - our nearest), with a small bias to shorten our second-nearest
    # and avoid positions that allow the opponent to get strictly closer to the best resource.
    best_dx, best_dy, best_val = 0, 0, -10**18
    our_md0, our_sd0 = min_dists(sx, sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        opp_md, _ = min_dists(ox, oy)
        our_md, our_sd = min_dists(nx, ny)

        # If we can reach a resource at least as fast as opponent, prioritize that.
        # Otherwise, still try to widen the distance gap (denial).
        gap = (opp_md - our_md)
        widen_penalty = 0
        # Denial check: does our move bring the opponent relatively closer to the nearest resource than we are?
        # (approx) compare nearest resource from each position without changing opponent
        if gap < 0 and our_md <= our_sd0:
            widen_penalty = 0.5

        # Bias to keep moving toward center of our side (deterministic, breaks ties)
        center_bias = -abs(nx - (w // 2)) - abs(ny - (h // 2))

        val = gap * 10.0 + (our_sd0 - our_sd) + center_bias - widen_penalty
        if val > best_val or (val == best_val and (dx, dy) < (best_dx, best_dy)):
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]