def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles)

    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        ndx = 0 if sx == tx else (1 if tx > sx else -1)
        ndy = 0 if sy == ty else (1 if ty > sy else -1)
        return [ndx, ndy]

    # Choose move that maximizes our advantage over opponent for the best available resource.
    best_move = [0, 0]
    best_val = -10**18

    # Pre-rank resources from our current position (deterministic).
    ranked = []
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # primary: opponent distance advantage; secondary: our closeness; tertiary: stable tie-break by coordinates
        ranked.append(((od - sd), -sd, rx, ry, od, sd))
    ranked.sort(reverse=True)

    # Evaluate each legal move against top few resources to stay fast.
    topk = ranked[:6]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        # If we can immediately take a resource next, strongly prefer.
        immediate = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                immediate = 1000000
                break

        # Maximize our advantage for the best target.
        # Slightly penalize moves that increase distance to the currently best target.
        val = immediate
        for (adv0, negsd0, rx, ry, od, sd0) in topk:
            sd1 = cheb(nx, ny, rx, ry)
            od1 = od  # opponent position unchanged this turn
            adv = od1 - sd1
            # Prefer targets where we are at least competitive; also prefer reducing our distance.
            val += (adv * 1000) + ((-sd1) * 5)

            # If opponent is closer by a lot, add a smaller penalty unless we improve.
            if adv < 0:
                val += adv * 2

        # Small bias to reduce oscillation: prefer staying only if already best.
        if dx == 0 and dy == 0:
            val -= 1

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [best_move[0], best_move[1]]