def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep_cell(r):
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (int(q[0]), int(q[1]))
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (int(r[0]), int(r[1]))
        return None

    rpos = []
    for r in resources:
        q = rep_cell(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)

    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        # Steal heuristic: prefer moves where you become closer to some resource
        # than the opponent, especially for resources currently advantaged to them.
        steal_best = -10**9
        closest_self = 10**9
        closest_opp = 10**9
        for rx, ry in rpos:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            gain = do - ds  # positive means you are closer than opponent
            if gain > steal_best:
                steal_best = gain
            if ds < closest_self:
                closest_self = ds
            if do < closest_opp:
                closest_opp = do

        # Secondary: if no steal advantage, still move toward resources the opponent is racing
        # and away from being directly closest to the same.
        tie_break = (closest_self, -steal_best, -closest_opp, ox - nx, oy - ny, dx, dy)
        score = (steal_best, -closest_self, closest_opp)
        key = (-score[0], score[1], -score[2], tie_break)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best else [0, 0]