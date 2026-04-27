def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx
            ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    if not resources:
        # No resources: drift to center-ish while staying deterministic and obstacle-aware
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**9
        for dx, dy, nx, ny in moves:
            d = cheb(nx, ny, tx, ty)
            v = -d
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Value: prefer positions that are much better than opponent across all resources (deterministic)
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in moves:
        val = 0.0
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # advantage term + slight push to reduce our distance
            val += (do + 1) / (ds + 1)  # higher when we are closer than opponent
            val -= 0.07 * ds
        # Tie-break deterministically: prefer not moving, then smallest dx, then smallest dy
        tie = (0 if dx == 0 and dy == 0 else 1, abs(dx), abs(dy), dx, dy)
        if val > best_val + 1e-12:
            best_val = val
            best_move = (dx, dy)
            best_tie = tie
        elif abs(val - best_val) <= 1e-12:
            try:
                if tie < best_tie:
                    best_move = (dx, dy)
                    best_tie = tie
            except:
                best_move = (dx, dy)
    return [best_move[0], best_move[1]]