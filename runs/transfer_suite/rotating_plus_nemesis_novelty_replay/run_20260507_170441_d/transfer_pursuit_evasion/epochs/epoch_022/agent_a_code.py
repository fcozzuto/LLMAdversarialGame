def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x = int(o[0]); y = int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def is_pursuer(role):
        r = str(role or "").lower()
        return ("purs" in r) or ("tag" in r) or ("hunter" in r) or ("search" in r)

    self_role = observation.get("self_role", "")
    opp_role = observation.get("opponent_role", "")
    self_is_p = is_pursuer(self_role)
    opp_is_p = is_pursuer(opp_role)

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    bestv = None

    if self_is_p:
        if res:
            # Move toward nearest resource
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if not ok(nx, ny):
                    continue
                d = min(dist2(nx, ny, rx, ry) for rx, ry in res)
                score = d
                if bestv is None or score < bestv:
                    bestv = score
                    best = [dx, dy]
        else:
            # Otherwise chase opponent
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if not ok(nx, ny):
                    continue
                score = dist2(nx, ny, ox, oy)
                if bestv is None or score < bestv:
                    bestv = score
                    best = [dx, dy]
    else:
        # Evade: move away from opponent; if opponent isn't pursuer, still slightly prefer resources
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            away = dist2(nx, ny, ox, oy)
            if res and not opp_is_p:
                near = min(dist2(nx, ny, rx, ry) for rx, ry in res)
                score = (-away) + 0.15 * near  # maximize away, break ties toward resources
            else:
                score = -away  # maximize away
            if bestv is None or score < bestv:
                bestv = score
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best