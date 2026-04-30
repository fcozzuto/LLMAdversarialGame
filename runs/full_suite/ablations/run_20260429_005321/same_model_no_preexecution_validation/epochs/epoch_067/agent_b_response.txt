def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obs = {(int(x), int(y)) for x, y in obstacles]
    res = [(int(x), int(y)) for x, y in resources]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    def obs_near(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                c += 1
        return c

    # If no resources: move to a safe region while keeping opponent at distance.
    if not res:
        best = (0, 0); bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            dcent = cheb(nx, ny, w // 2, h // 2)
            dopp = cheb(nx, ny, ox, oy)
            v = 2 * dopp - dcent - 3 * obs_near(nx, ny)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose a target resource we can reach relatively earlier than the opponent.
    best_target = res[0]
    best_key = None
    for rx, ry in res:
        dme = cheb(sx, sy, rx, ry)
        dob = cheb(ox, oy, rx, ry)
        # Prefer small (dme - 0.9*dob); tie-break by smaller dme then by coordinates.
        key = (dme - 9 * dob / 10.0, dme, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)
    tx, ty = best_target

    # Score each candidate move: get closer to target, simultaneously reduce opponent's advantage, avoid obstacles.
    best = (0, 0); bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        dme_now = cheb(sx, sy, tx, ty)
        dme_next = cheb(nx, ny, tx, ty)
        dob_now = cheb(ox, oy, tx, ty)
        # Approximate opponent ability: assume opponent can move one step similarly (use best-case reduction).
        dob_next_best = min(cheb(ox + adx, oy + ady, tx, ty) for adx, ady in dirs if inb(ox + adx, oy + ady) and (ox + adx, oy + ady) not in obs)
        # Higher is better.
        v = 5 * (dme_now - dme_next) + 2.5 * (dob_now - dob_next_best) - 4 * obs_near(nx, ny)
        # Slightly discourage moving closer to opponent unless it helps target.
        v -= 0.4 * cheb(nx, ny, ox, oy)
        # Encourage staying within bounds already handled; tie-break deterministically by move ordering preference.
        if v > bestv:
            bestv = v; best = (dx, dy)
    return [int(best[0]), int(best[1])]