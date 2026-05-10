def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    ordered_resources = sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1]))
    best_move = [0, 0]
    best_val = -10**30
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        move_val = 0.0
        # Prefer immediate capture and states that maintain a lead over the opponent.
        for rx, ry in ordered_resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # larger is better
            cap = 3.0 if (nx, ny) == (rx, ry) else 0.0
            # Deny: if opponent is closer, being closer too is worse; if we are closer, it is good.
            deny = -0.35 * max(0, -lead)
            # Small tie-break shaping: slightly prefer nearer-to-opponent-competition point
            center_bias = 0.05 * cheb(nx, ny, ox, oy)
            v = cap + 2.6 * lead - 0.45 * ds + deny + center_bias
            if v > move_val:
                move_val = v

        # Tiny lookahead: if we capture now, keep stable; otherwise, prefer reducing our distance to the best resource.
        if move_val > 0.2:
            # Also ensure not walking into a situation where opponent can immediately capture a resource we can deny next.
            # Evaluate opponent's potential capture one step from now.
            threat = 0.0
            for rx, ry in ordered_resources[:6]:
                do0 = cheb(ox, oy, rx, ry)
                if do0 <= 1 and (rx, ry) != (nx, ny):
                    threat -= 0.6
            move_val += threat

        if move_val > best_val + 1e-12:
            best_val = move_val
            best_move = [dx, dy]
        elif abs(move_val - best_val) <= 1e-12:
            # Deterministic tie-break: lexicographic preference with slight bias towards staying.
            if best_move == [0, 0]:
                continue
            # Prefer [0,0], then larger dx, then smaller dy deterministically.
            if best_move != [0, 0] and [dx, dy] == [0, 0]:
                best_move = [dx, dy]
            else:
                if (dx, dy) < (best_move[0], best_move[1]):
                    best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]