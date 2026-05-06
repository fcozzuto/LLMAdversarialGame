def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = {(int(p[0]), int(p[1])) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    for r in resources:
        if int(r[0]) == sx and int(r[1]) == sy:
            return [0, 0]

    if not resources:
        return [0, 0]

    best_u = None
    best_m = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs_set:
            continue

        self_best_d = 10**9
        opp_best_d = 10**9
        best_adv = -10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if sd < self_best_d: self_best_d = sd
            if od < opp_best_d: opp_best_d = od
            adv = od - sd  # positive means we race ahead
            if adv > best_adv: best_adv = adv

        # Resource race first; if can't win any, still move to reduce our distance while worsening opponent's best.
        u = (best_adv * 1000.0) - (self_best_d * 1.0) - ((opp_best_d - self_best_d) * 0.2)
        if best_u is None or u > best_u or (u == best_u and (dx, dy) < (best_m[0], best_m[1])):
            best_u = u
            best_m = [dx, dy]

    return best_m