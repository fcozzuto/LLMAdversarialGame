def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        if dx < 0: dx = -dx
        dy = by - ay
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Deterministic obstacle proximity penalty (discourage stepping next to blocks)
    def near_block_pen(x, y):
        pen = 0
        for (bx, by) in obs:
            d = cheb(x, y, bx, by)
            if d == 0:
                pen -= 1000
            elif d == 1:
                pen -= 3
        return pen

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Contention: prefer moves that maximize (opp_cheb - self_cheb) to a resource.
        val = near_block_pen(nx, ny)
        # Secondary pressure: move to interfere with opponent corridor by nudging toward them if no winning race.
        opp_push = -cheb(nx, ny, ox, oy)
        val += 0.5 * opp_push

        local_best = -10**18
        for rx, ry in resources:
            self_t = cheb(nx, ny, rx, ry)
            opp_t = cheb(ox, oy, rx, ry)
            # If we can arrive strictly earlier, strongly prefer it; if equal, prefer still-advantageous resource.
            delta = opp_t - self_t
            tie = 0
            if delta == 0:
                tie = 1 if (self_t != 0) else 0
            # Small preference for being closer when races are similar.
            val_r = 10 * delta - 0.2 * self_t + 0.3 * tie
            if val_r > local_best:
                local_best = val_r

        val += local_best
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]