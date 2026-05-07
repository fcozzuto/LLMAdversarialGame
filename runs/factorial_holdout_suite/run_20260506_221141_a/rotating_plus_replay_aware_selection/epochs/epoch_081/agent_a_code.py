def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = 7 if sx < 4 else 0
        ty = 7 if sy < 4 else 0
        best, bestv = [0, 0], -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            v = -(cheb(nx, ny, tx, ty))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_move, best_val = [0, 0], -10**18
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not legal(nx, ny):
            continue

        # Pick the resource that gives maximal immediate advantage from (nx,ny)
        cur_best_adv = -10**18
        cur_best_dist = 10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_me
            if adv > cur_best_adv or (adv == cur_best_adv and d_me < cur_best_dist):
                cur_best_adv = adv
                cur_best_dist = d_me

        # Higher is better: try to secure a resource that opponent is farther from.
        # Tie-break deterministically by preferring smaller self distance.
        val = (cur_best_adv * 1000) - cur_best_dist
        if val > best_val:
            best_val = val
            best_move = [mdx, mdy]

    return best_move