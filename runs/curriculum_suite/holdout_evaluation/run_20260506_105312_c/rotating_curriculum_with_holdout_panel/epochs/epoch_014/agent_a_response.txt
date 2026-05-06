def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Score moves by best "advantage" over opponent for contested resources,
    # with fallback to closest-resource progress.
    best_move = (0, 0)
    best_val = -10**18
    fallback_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Advantage over opponent: positive means we are closer (chebyshev) to that resource.
        move_best_adv = -10**18
        move_closest = 10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # prefer states where we strictly beat opponent; discourage if opponent is already winning.
            adv = opd - myd
            if adv < -1:
                continue
            # small bonus for being close even if slightly contested
            proximity = -myd
            # prioritize likely grabs: larger adv, then closer
            val = adv * 20 + proximity
            if myd < move_closest:
                move_closest = myd
            if val > move_best_adv:
                move_best_adv = val

        # Fallback: if no clear advantage, just go toward nearest resource.
        if move_best_adv <= -10**17:
            val = -move_closest
            if val > fallback_val:
                fallback_val = val
                best_move = (dx, dy)
            continue

        # Main: maximize advantage; break ties by closeness and then deterministic prefer earlier deltas.
        if move_best_adv > best_val:
            best_val = move_best_adv
            best_move = (dx, dy)
        elif move_best_adv == best_val:
            if cheb(nx, ny, *resources[0]) < cheb(sx + best_move[0], sy + best_move[1], *resources[0]):
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]