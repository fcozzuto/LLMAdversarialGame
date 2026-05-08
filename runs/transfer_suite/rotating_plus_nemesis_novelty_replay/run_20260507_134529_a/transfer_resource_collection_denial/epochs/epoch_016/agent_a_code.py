def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    # Prefer staying close to promising resources; break ties deterministically.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0

        # Score: maximize advantage in reaching resources, with small preference for near pickups.
        # Also add mild "opponent denial": favor resources where opponent is relatively close.
        local_best = -10**18
        local_tiebreak = 10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive: we are closer
            # Near-term pickup bias and contested-resource bias
            score = adv * 100 - myd * 3 + opd
            if myd == 0:
                score += 1000000
            if myd == 1:
                score += 2000
            if score > local_best or (score == local_best and myd < local_tiebreak):
                local_best = score
                local_tiebreak = myd

        # If opponent is adjacent to some resource, prioritize moving toward the closest such contested item.
        contested = 0
        best_cont = 10**18
        for rx, ry in resources:
            opd = cheb(ox, oy, rx, ry)
            if opd <= 2:
                contested += 1
                md = cheb(nx, ny, rx, ry)
                if md < best_cont:
                    best_cont = md
        score2 = local_best + (contested * 15) - best_cont

        # Deterministic tie-break: prefer smaller dx, then smaller dy (lexicographic on (dx,dy)).
        if score2 > best_score or (score2 == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score2
            best_move = [dx, dy]

    return best_move