def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh_obs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def obstacle_pen(x, y):
        if (x, y) in occ:
            return -10**9
        pen = 0
        for dx, dy in neigh_obs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in occ:
                pen -= 6
        return pen

    # Pick a primary contested target: maximize how much closer we are than opponent
    best_t = None
    best_contest = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        lead = opd - myd  # positive if we're closer
        # Prefer resources where we're not only closer but also reasonably near overall
        cont = lead * 100 - myd
        if cont > best_contest:
            best_contest = cont
            best_t = (rx, ry)

    # Secondary target: avoid getting stuck if opponent is closer to primary too strongly
    secondary = None
    if len(resources) > 1:
        best2 = -10**18
        for rx, ry in resources:
            if (rx, ry) == best_t:
                continue
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            cont = (opd - myd) * 100 - myd
            if cont > best2:
                best2 = cont
                secondary = (rx, ry)

    # If opponent is much closer to primary, pivot to secondary
    rx1, ry1 = best_t
    if best_contest < 0 and secondary is not None:
        rx1, ry1 = secondary

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        pen = obstacle_pen(nx, ny)
        if pen < -10**8:
            continue

        myd = cheb(nx, ny, rx1, ry1)
        opd = cheb(ox, oy, rx1, ry1)
        # If we can make the distance advantage, emphasize it strongly.
        score = (opd - myd) * 120 - myd * 2 + pen

        # Add small term to not chase directly into opponent when contesting
        d_op = cheb(nx, ny, ox, oy)
        score += d_op * 0.3

        # Mild tie-break: stay oriented toward primary vs drift
        score -= 0.05 * cheb(nx, ny, rx1, ry1)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]