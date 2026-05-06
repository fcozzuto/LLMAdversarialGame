def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = [(int(p[0]), int(p[1])) for p in resources]
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for rx, ry in res:
        if rx == sx and ry == sy:
            return [0, 0]

    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Moves: allow diagonals and staying
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (-(10**18), 0, 0)  # (adv, -opp_d, self_d)
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        self_d_min = None
        opp_d_min_for_that = None
        best_adv_here = -(10**18)
        best_opp_d_for_adv = 10**18
        best_self_d_for_adv = 10**18

        for rx, ry in res:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - self_d  # positive means we can arrive earlier (or tie)
            if adv > best_adv_here or (adv == best_adv_here and (opp_d < best_opp_d_for_adv or (opp_d == best_opp_d_for_adv and self_d < best_self_d_for_adv))):
                best_adv_here = adv
                best_opp_d_for_adv = opp_d
                best_self_d_for_adv = self_d

        cand = (best_adv_here, -best_opp_d_for_adv, best_self_d_for_adv)
        if cand > best:
            best = cand
            best_move = [dx, dy]

    return best_move