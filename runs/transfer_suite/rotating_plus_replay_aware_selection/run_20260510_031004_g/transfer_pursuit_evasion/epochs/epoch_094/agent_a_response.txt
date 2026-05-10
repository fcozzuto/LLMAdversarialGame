def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("purs" in opp_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    obs_list = list(obstacles)
    def obs_dist(x, y):
        if not obs_list: return 99
        md = 99
        for (oxb, oyb) in obs_list:
            d = abs(oxb - x) + abs(oyb - y)
            if d < md: md = d
            if md == 0: break
        return md

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if self_is_pursuer and nx == ox and ny == oy:
            return [dx, dy]

        d = cheb(nx, ny)
        od = obs_dist(nx, ny)

        if self_is_pursuer:
            # primary: closer in Chebyshev; tie: keep away from obstacles; tie: deterministic preference
            key = (d, -od, abs(dx) + abs(dy), dx, dy)
        else:
            # primary: farther in Chebyshev; tie: keep away from obstacles; tie: deterministic preference
            key = (-d, -od, abs(dx) + abs(dy), -dx, -dy)

        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best