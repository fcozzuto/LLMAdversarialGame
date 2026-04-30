def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # If standing on a resource, stay to collect.
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    # If no resources known, head to opponent-opposed center-ish point: maximize distance from obstacles and progress to opponent.
    if not resources:
        best = (0, 0, -10**18)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            step_free = 0
            for ddx, ddy in deltas:
                tx, ty = nx + ddx, ny + ddy
                if valid(tx, ty): step_free += 1
            val = (cheb(ox, oy, nx, ny) * 3) + step_free
            if val > best[2]:
                best = (dx, dy, val)
        return [best[0], best[1]]

    # Antagonistic targeting: choose a resource where we can gain the most relative closeness vs opponent.
    # Then one-step choose move that maximizes that gain after moving.
    best_move = (0, 0, -10**30)
    for mdx, mdy in deltas:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        # Free-space bonus to avoid getting stuck near obstacles.
        free = 0
        for ddx, ddy in deltas:
            if valid(nx + ddx, ny + ddy):
                free += 1

        # For each resource, compute relative advantage we would have after this move.
        # Advantage = (opp_dist - self_dist): bigger means we are closer than opponent.
        best_adv = -10**30
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            # Prefer immediate capture potential and also prefer reducing our distance even if opponent is closer.
            if sd == 0:
                adv += 10000
            best_adv = adv if adv > best_adv else best_adv

        # Secondary tie-break: reduce our distance to the best resource (negative cost).
        # Also mildly discourage moving away from all resources by penalizing minimum self distance.
        min_sd = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < min_sd: min_sd = d

        val = (best_adv * 1000) - (min_sd * 10) + free
        if val > best_move[2]:
            best_move = (mdx, mdy, val)

    return [best_move[0], best_move[1]]