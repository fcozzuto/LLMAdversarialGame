def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    if not resources:
        # deterministic fallback: retreat toward our corner while staying away from opponent
        tx, ty = 0, 0
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            v = (cheb(ox, oy, nx, ny) * 3) - (cheb(nx, ny, tx, ty))
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        # Evaluate move by (1) how many resources we can secure first, (2) how close we are to the best one,
        # (3) how much we delay opponent.
        my_best = 10**9
        opp_best = 10**9
        secure = 0
        lead_sum = 0
        denier = 0
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            if d_my < my_best:
                my_best = d_my
            if d_op < opp_best:
                opp_best = d_op
            if d_my <= d_op - 1:
                secure += 1
                lead_sum += (d_op - d_my)
            # deny: if after we move, opponent cannot reach many cells as fast as us
            if d_op <= d_my:
                denier += 1
        # Prefer getting ahead while shrinking opponent lead; discourage moves that let many resources be "equally reachable"
        v = (secure * 200) + (lead_sum * 10) - (denier * 25) + (opp_best - my_best) * 8 - my_best * 2
        if v > bestv:
            bestv = v; best = [dx, dy]
    return best