def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] or []
    obstacles = set(tuple(p) for p in (observation["obstacles"] or []))

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                moves.append((dx, dy))

    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        oppd = abs(nx - ox) + abs(ny - oy)
        if resources:
            # Choose resource preference: closer to us, but also prefer ones where we are not behind opponent.
            score = 0
            best_r = None
            best_r_val = -10**18
            for rx, ry in resources:
                d1 = abs(nx - rx) + abs(ny - ry)
                d2 = abs(ox - rx) + abs(oy - ry)
                # If we are not closer than opponent, reduce attractiveness.
                rel = d2 - d1
                val = -d1 + 0.8 * rel
                if val > best_r_val:
                    best_r_val = val
                    best_r = (rx, ry)
            # Final value balances reaching the resource and keeping distance from opponent.
            score = best_r_val + 0.06 * oppd
        else:
            # No resources: just keep distance and avoid obstacles.
            score = 0.02 * oppd
        # Tie-breaker: prefer moves that reduce manhattan distance to opponent (more pressure when tied).
        tiebreak = - (abs(nx - ox) + abs(ny - oy))
        val = score + 0.001 * tiebreak
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]