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

    if not resources:
        best = (0, 0)
        bestv = -10**18
        tx, ty = w - 1, h - 1
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            # Prefer increasing opponent distance while drifting to our far corner.
            v = d_opp * 120 - (abs(nx - tx) + abs(ny - ty))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # One-step lookahead scoring for grabbing or denying.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        d_opp_move = cheb(nx, ny, ox, oy)
        v = d_opp_move * -1  # don't chase too hard; stay safe

        # Evaluate resources: favor those we can reach sooner, penalize those they can reach sooner.
        # Deterministic aggregation with early pruning by top candidates.
        scored = []
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            scored.append((od - sd, sd, od))
        scored.sort(reverse=True, key=lambda t: (t[0], -t[1], -t[2]))

        # Use a small fixed prefix to keep deterministic and concise.
        for i in range(min(5, len(scored))):
            delta, sd, od = scored[i]
            if delta > 0:
                # We are closer now; grabbing is good.
                v += delta * 180 - sd * 8
            else:
                # They are closer; denying by approaching still helps.
                v += delta * 70 - od * 2 + sd * 2

        # Small preference for moves that reduce closest resource distance for stability.
        best_closest = scored[0][1] if scored else 0
        v += -best_closest * 3

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]