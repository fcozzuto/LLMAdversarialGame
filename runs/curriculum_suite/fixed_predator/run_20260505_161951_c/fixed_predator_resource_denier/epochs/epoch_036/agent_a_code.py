def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    if not resources:
        tx, ty = (w - 1) if x < w // 2 else 0, (h - 1) if y < h // 2 else 0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy) * 1000 - cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best = [0, 0]
    bestv = -10**18
    centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        self_to_opp = cheb(nx, ny, ox, oy)
        # For each move, try to (1) capture a resource we beat, else (2) deny a resource they can beat.
        best_gain = -10**18
        best_capture_dist = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # capture if we can arrive no later than opponent; deny if opponent can arrive much earlier.
            if ds <= do:
                gain = (do - ds + 1) * 2000 - (abs(nx - rx) + abs(ny - ry))
                if gain > best_gain or (gain == best_gain and ds < best_capture_dist):
                    best_gain = gain
                    best_capture_dist = ds
            else:
                # deny: head toward resources where opponent is strongly favored
                deny = (do - ds) * 120 - (abs(nx - rx) + abs(ny - ry))
                if deny > best_gain:
                    best_gain = deny
        # Add anti-trap / anti-symmetry: keep distance from opponent and mildly favor center to avoid cornering into obstacles.
        center_bias = -((nx - centerx) * (nx - centerx) + (ny - centery) * (ny - centery)) * 0.02
        dist_term = self_to_opp * 8
        v = best_gain + dist_term + center_bias
        # Deterministic tie-break: prefer moves closer to being "toward" best resource relative to opponent
        if v > bestv:
            bestv = v
            best = [dx, dy]
        elif v == bestv:
            # deterministic: lexical order on (dx,dy)
            if (dx, dy) < (best[0], best[1]):
                best = [dx, dy]
    return [int(best[0]), int(best[1])]