def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep_pos(obj):
        if isinstance(obj, dict):
            q = obj.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (q[0], q[1])
        if isinstance(obj, (list, tuple)) and len(obj) >= 2:
            return (obj[0], obj[1])
        return None

    rpos = []
    for r in resources:
        q = rep_pos(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)

    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None  # (score, -closest_self_d, -best_resource_x, -best_resource_y, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        closest_self = 10**9
        best_gain = -10**9
        best_rx = 0
        best_ry = 0
        for rx, ry in rpos:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            closest_self = min(closest_self, self_d)
            gain = opp_d - self_d  # positive means we are closer than opponent
            if gain > best_gain or (gain == best_gain and (self_d < closest_self or (self_d == closest_self and (rx, ry) < (best_rx, best_ry)))):
                best_gain = gain
                best_rx, best_ry = rx, ry

        # Prefer positions that secure a favorable resource, then get closer overall.
        score = best_gain * 100 - closest_self
        cand = (score, -closest_self, -best_rx, -best_ry, dx, dy)
        if best is None or cand > best:
            best = cand

    return [int(best[4]), int(best[5])]