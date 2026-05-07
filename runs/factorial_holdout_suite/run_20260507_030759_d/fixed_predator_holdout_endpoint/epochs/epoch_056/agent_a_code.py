def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    if not resources:
        return [0, 0]

    obst = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            continue

        best_adv = None
        best_my_d = 0
        best_opp_d = 0

        opp_closer_count = 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if opd < myd:
                opp_closer_count += 1
            adv = opd - myd
            if best_adv is None or adv > best_adv:
                best_adv = adv
                best_my_d = myd
                best_opp_d = opd
            elif adv == best_adv:
                if myd < best_my_d or (myd == best_my_d and opd < best_opp_d):
                    best_my_d = myd
                    best_opp_d = opd

        key = (best_adv, -best_my_d, -best_opp_d, -opp_closer_count)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]