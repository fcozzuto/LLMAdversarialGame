def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        target = (w - 1, h - 1)
    else:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            race = do - ds  # want positive: we're closer than opponent
            # Prefer positive races; then shorter ds; then deterministic tie by coords
            key = (-race, ds, rx, ry)  # minimizing negative race => maximizing race
            if best is None or key < best[0]:
                best = (key, rx, ry)
        _, tx, ty = best
        target = (tx, ty)

    def opp_greedy_dist():
        px, py = ox, oy
        best_d = None
        best_move = None
        for dx, dy in deltas:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = cheb(nx, ny, target[0], target[1])
            if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
                best_d = d
                best_move = (dx, dy)
        if best_d is None:
            return cheb(px, py, target[0], target[1])
        return best_d

    do_next = opp_greedy_dist()

    best_delta = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds_next = cheb(nx, ny, target[0], target[1])
        # Higher is better: being closer than opponent after our move.
        race_after = do_next - ds_next
        # Small penalty for moving away from opponent (helps contention)
        opp_dist_after = cheb(nx, ny, ox, oy)
        # Obstacle proximity penalty (prefer not to hug obstacles if equal)
        near_obs = 0
        for adx, ady in deltas:
            ax2, ay2 = nx + adx, ny + ady
            if inb(ax2, ay2) and (ax2, ay2) in obs:
                near_obs += 1
        val = (race_after, -ds_next, -opp_dist_after, -near_obs)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_delta):
            best_val = val
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]