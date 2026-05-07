def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        best, bestv = [0, 0], -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, cx, cy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_move, best_score = [0, 0], -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        move_score = 0.0
        # Immediate pickup bonus
        if (nx, ny) in obstacles:
            move_score -= 1e9

        # Evaluate best resource matchup from this position.
        best_for_pos = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)

            # Our advantage increases when we can arrive no later than opponent.
            # Also slightly prefer closer resources to reduce dithering.
            if d_me < d_opp:
                base = 50 - d_me
            elif d_me == d_opp:
                base = 5 - d_me
            else:
                base = -20 - (d_me - d_opp) - d_me * 0.1

            # Tie-break for determinism: prefer lower coordinates among equal scores.
            coord_bias = -(rx * 0.01 + ry * 0.001)
            s = base + coord_bias
            if s > best_for_pos:
                best_for_pos = s

        move_score += best_for_pos

        # Mild repulsion from opponent to avoid getting stalled by sweep pressure
        move_score -= 0.15 * cheb(nx, ny, ox, oy)

        if move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]

    return best_move