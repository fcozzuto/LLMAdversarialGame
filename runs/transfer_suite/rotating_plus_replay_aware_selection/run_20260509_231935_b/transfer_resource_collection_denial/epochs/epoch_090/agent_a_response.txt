def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation.get("resources", []) or []
    obs_raw = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obs_raw if p and len(p) >= 2}
    resources = [(p[0], p[1]) for p in res if p and len(p) >= 2]

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

    def count_near(x, y):
        # discourage stepping adjacent to obstacles to reduce getting stuck/collisions
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        # fall back: minimize distance to opponent's position while not hitting obstacles
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -cheb(nx, ny, ox, oy) - 0.3 * count_near(nx, ny)
            if v > bestv or (v == bestv and (dx, dy) < tuple(best)):
                bestv = v
                best = [dx, dy]
        return best

    # Choose move by evaluating 1-step improvement toward resources where we lead opponent
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        step_val = -0.25 * (abs(nx - sx) + abs(ny - sy)) - 0.6 * count_near(nx, ny)
        # If we already are on a resource (rare after move), treat as high value
        if (nx, ny) in obstacles:
            continue
        # Evaluate best resource to target from this candidate position
        local_best = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            lead = opd - myd  # positive means we are closer (or arrive earlier)
            v = 18.0 * lead - myd - 0.15 * (myd == 0) - 0.02 * (rx + ry)
            # Strongly prioritize immediate pickups and avoid picking resources we are behind on
            if myd == 0:
                v += 100.0
            local_best = v if v > local_best else local_best
        step_val += local_best
        if step_val > best_val:
            best_val = step_val
            best_move = [dx, dy]
        elif step_val == best_val:
            # deterministic tiebreak: prefer lexicographically smallest (dx,dy)
            if (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]
    return best_move