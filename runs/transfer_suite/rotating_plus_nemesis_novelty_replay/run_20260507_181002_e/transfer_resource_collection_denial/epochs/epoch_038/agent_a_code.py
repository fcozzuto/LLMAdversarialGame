def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return int(v[0]), int(v[1])
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
    if not res:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Denial-aware target: prefer resources where opponent is relatively far.
    opp = (ox, oy)
    me = (sx, sy)
    best = None
    for cell in res:
        sd = man(me, cell)
        od = man(opp, cell)
        # Strongly favor "harder for opponent than for me", but keep sd small.
        score = (od - sd) * 100 - sd
        key = (score, -sd, -cell[0], -cell[1])
        if best is None or key > best[0]:
            best = (key, cell)
    target = best[1]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (10**9, -10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d_to_target = man((nx, ny), target)
        # Extra preference: don't step toward a cell the opponent is overwhelmingly closer to.
        opp_d = man(opp, target)
        # If opponent is very close to target, prefer moves that reduce our distance more aggressively.
        urgency = (opp_d - d_to_target)
        key = (d_to_target, -urgency, dx, dy)
        if key < best_move:
            best_move = key
            best_pair = (dx, dy)

    return [int(best_pair[0]), int(best_pair[1])]