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
    ox, oy = to_xy(observation.get("opponent_position", [0, 0])) or (0, 0)

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

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_delta = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        ns = (nx, ny)
        if not res:
            val = (-man(ns, (ox, oy)), -man(ns, (sx, sy)))
        else:
            # Pick the resource that gives maximum advantage for the current move.
            # tie-break: prefer smaller own distance, then smaller x,y deterministically.
            best_target_val = None
            for t in res:
                self_d = man(ns, t)
                opp_d = man((ox, oy), t)
                # advantage > 0 means we can reach earlier (or at least closer than opponent)
                adv = opp_d - self_d
                key = (adv, -self_d, -abs(t[0] - sx) - abs(t[1] - sy), -t[0], -t[1])
                if best_target_val is None or key > best_target_val:
                    best_target_val = key
            val = best_target_val
        if best_val is None or val > best_val:
            best_val = val
            best_delta = (dx, dy)

    dx, dy = best_delta
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [dx, dy]