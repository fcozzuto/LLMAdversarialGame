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
            x, y = t
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    obs = set()
    for o in obstacles:
        t = to_xy(o)
        if t is not None:
            x, y = t
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if res:
        best = None
        best_key = None
        for x, y in res:
            ds = abs(x - sx) + abs(y - sy)
            do = abs(x - ox) + abs(y - oy)
            # Prefer resources where we are closer than opponent (denier-aware), but still prioritize proximity.
            key = (ds - 0.9 * do, ds, do, x, y)
            if best_key is None or key < best_key:
                best_key = key
                best = (x, y)
        tx, ty = best
    else:
        # No visible resources: go to the more "likely" corner (opposite of opponent side) to search.
        tx, ty = ((w - 1, 0) if (ox == 0 and oy == h - 1) else (0, h - 1))
        if ox == 0 and oy == 0:
            tx, ty = (w - 1, h - 1)
        if ox == w - 1 and oy == h - 1:
            tx, ty = (0, 0)

    def score_move(nx, ny):
        if (nx, ny) in obs:
            return 10**9
        # Encourage getting closer to target, discourage getting closer to opponent's target area.
        d1 = abs(tx - nx) + abs(ty - ny)
        d2 = abs(tx - ox) + abs(ty - oy)
        # Also add slight penalty for stepping into obstacle-adjacent positions (stabilize).
        adj_pen = 0
        for dx, dy in dirs:
            ax, ay = nx + dx, ny + dy
            if in_bounds(ax, ay) and (ax, ay) in obs:
                adj_pen += 1
        return d1 - 0.2 * d2 + 0.3 * adj_pen

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny):
            candidates.append((score_move(nx, ny), dx, dy))
    candidates.sort()
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]