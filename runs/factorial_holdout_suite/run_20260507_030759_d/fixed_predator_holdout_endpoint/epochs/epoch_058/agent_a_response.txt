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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue

        best_adv = -10**9
        best_myd_for_adv = 10**9
        win_count = 0  # how many resources we are at least as close to as opponent

        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if opd <= myd:
                win_count += 1
            if adv > best_adv or (adv == best_adv and myd < best_myd_for_adv):
                best_adv = adv
                best_myd_for_adv = myd

        key = (best_adv, win_count, -best_myd_for_adv, -abs(nx - ox) - abs(ny - oy))
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]