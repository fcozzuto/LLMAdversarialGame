def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        # retreat/deny: move to maximize distance from opponent after move
        best = None
        bestv = -10**9
        for dx, dy, nx, ny in moves:
            v = abs(nx - ox) + abs(ny - oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick the move that maximizes our advantage after reaching a good resource, with slight tie-break to reduce opponent access.
    # We also avoid moves that move us away from any remaining resource too much.
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy, nx, ny in moves:
        # Precompute our and opponent distances to each resource
        # Heuristic chooses the resource where we improve most relative to opponent.
        best_r_val = -10**18
        best_r_dist = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # advantage: positive means we are closer
            adv = od - sd
            # discourage targeting resources we are far from; prefer closeness once advantage exists
            close = -sd
            # if opponent is extremely close, prefer resources where we can "flip" that race quickly
            flip = (od - sd) * 2
            r_val = flip + close
            # tie-break: prefer smaller our distance
            if r_val > best_r_val or (r_val == best_r_val and sd < best_r_dist):
                best_r_val = r_val
                best_r_dist = sd
        # Overall move value: best resource advantage minus small penalty for being stuck far from all resources
        # (measure by average of a few nearest distances to avoid full-grid search)
        dists = []
        for rx, ry in resources:
            dists.append(man(nx, ny, rx, ry))
        dists.sort()
        nearest_avg = 0
        k = 3 if len(dists) >= 3 else len(dists)
        for i in range(k):
            nearest_avg += dists[i]
        nearest_avg = nearest_avg / k if k else 0
        # Extra denial term: reduce opponent's chance by moving toward where opponent is not already best
        opp_nearest = 10**9
        for rx, ry in resources:
            dd = man(ox, oy, rx, ry)
            if dd < opp_nearest:
                opp_nearest = dd
        deny = opp_nearest - best_r_dist  # positive => we target something nearer than opponent's nearest
        val = best_r_val + 0.25 * deny - 0.02 * nearest_avg

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]