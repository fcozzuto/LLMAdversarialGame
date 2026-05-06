def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # If no resources, drift to maximize distance from opponent while avoiding obstacles.
    if not resources:
        best = (-10**18, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            val = cheb(nx, ny, ox, oy)
            # tie-break: prefer moves that keep within bounds and are not blocked (already ensured)
            cand = (val, -abs(dx), -abs(dy))
            if cand > best:
                best = cand
                bx, by = dx, dy
        return [bx, by] if best != (-10**18, 0, 0) else [0, 0]

    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Score: try to find a resource we can reach closer than opponent.
        # advantage = opp_dist - self_dist (higher is better)
        best_adv = -10**18
        best_self_close = 10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and sd < best_self_close):
                best_adv = adv
                best_self_close = sd

        # Small secondary terms: prefer closer to that candidate resource; mildly avoid the opponent.
        dist_opp = cheb(nx, ny, ox, oy)
        val = best_adv * 1000 - best_self_close - dist_opp * 0.01
        cand = (val, -dx, -dy)
        if cand > best:
            best = cand
            bx, by = dx, dy

    return [bx, by] if best != (-10**18, 0, 0) else [0, 0]