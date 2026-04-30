def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = (0, 0)
        best_sc = -10**9
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h: 
                continue
            if (nx, ny) in obstacles:
                continue
            dopp = cheb(nx, ny, ox, oy)
            sc = doppel = doppel if False else dopp
            if sc > best_sc:
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]]

    best_target = resources[0]
    best_adv = -10**9
    best_selfd = 10**9
    for rx, ry in resources:
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and sd < best_selfd):
            best_adv = adv
            best_selfd = sd
            best_target = (rx, ry)

    rx, ry = best_target
    cur_sd = cheb(x, y, rx, ry)
    cur_od = cheb(ox, oy, x, y)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, rx, ry)
        nod = cheb(ox, oy, nx, ny)
        # Primary: get to a resource we're advantaged for (or at least don't lose it)
        # Secondary: avoid clustering too close to opponent.
        adv_after = cheb(ox, oy, rx, ry) - nsd
        score = (1000 * adv_after) - (10 * nsd)
        # Penalize moving closer to opponent
        if nod < cur_od:
            score -= (25 * (cur_od - nod))
        # Slightly prefer staying within bounds and not oscillating: reduce distance to opponent if already close?
        if cur_sd == 0:
            score += 5
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]