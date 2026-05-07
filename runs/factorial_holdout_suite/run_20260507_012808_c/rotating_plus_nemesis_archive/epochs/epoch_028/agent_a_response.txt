def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    if not res:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def clamp_move(nx, ny):
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            return sx, sy
        return nx, ny

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = clamp_move(sx + dx, sy + dy)
        self_d = 10**9
        opp_d = 10**9
        better_cnt = 0
        closest_self = None
        for rx, ry in res:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            if ds < self_d:
                self_d = ds
                closest_self = (rx, ry)
            if do < opp_d:
                opp_d = do
            if ds < do:
                better_cnt += 1
        # Prefer immediate advantage, then closer-next, then more resources favored to us, then tie-break toward moving
        adv = opp_d - self_d
        if closest_self is None:
            continue
        move_toward = abs(nx - closest_self[0]) + abs(ny - closest_self[1])
        score = (adv, -move_toward, better_cnt)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]