def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -(cheb(nx, ny, tx, ty))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Choose the resource that maximizes "I'm closer than opponent" after this move.
        # Prefer larger advantage; then smaller my distance to finish faster.
        best_cell = -10**18
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - my_d
            # Small bias to avoid standing still too long and to favor progress.
            progress = -(my_d)
            v = adv * 1000 + progress
            if v > best_cell:
                best_cell = v
        if best_cell > bestv:
            bestv = best_cell
            best = [dx, dy]

    return best