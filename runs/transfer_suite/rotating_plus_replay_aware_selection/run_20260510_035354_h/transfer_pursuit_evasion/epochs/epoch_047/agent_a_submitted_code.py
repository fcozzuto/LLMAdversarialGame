def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (0, 0)))
    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles if p is not None and len(p) >= 2}

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evader = ("evad" in self_role) or ("evader" in self_role)
    if ("evad" in opp_role) or ("evader" in opp_role):
        evader = False
    if "purs" in self_role:
        evader = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inside(x, y) and (x, y) not in obs
    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best = (10**9, (0, 0))
    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        if r is None or len(r) < 2: continue
        res_list.append((int(r[0]), int(r[1])))
    target = None
    if res_list:
        best_res = 10**9
        for rx, ry in res_list:
            d = dist(sx, sy, rx, ry)
            if d < best_res:
                best_res = d
                target = (rx, ry)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): 
            continue
        if target is not None:
            score = dist(nx, ny, target[0], target[1])
            # tie-break: prefer moves that increase distance from opponent if evader, else decrease
            oppd = dist(nx, ny, ox, oy)
            if evader:
                key = (score, -oppd)
            else:
                key = (score, oppd)
            if key < best[0:2]:
                best = (key[0] if True else key[0], (dx, dy))
        else:
            oppd = dist(nx, ny, ox, oy)
            score = -oppd if evader else oppd
            if (score, dx, dy) < best[0:2]:
                best = (score, (dx, dy))

    return best[1] if legal(sx + best[1][0], sy + best[1][1]) else [0, 0]