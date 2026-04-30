def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obs_set = set((p[0], p[1]) for p in obstacles)

    moves = [(-1,-1), (0,-1), (1,-1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obs_set:
            score = 10**9 + (abs(dx) + abs(dy))
        else:
            # Choose a target resource that we can reach more favorably than opponent.
            score = None
            for rx, ry in resources:
                sd = abs(rx - nx) + abs(ry - ny)
                od = abs(rx - ox) + abs(ry - oy)
                # Lower is better: prioritize reducing our distance and increasing theirs.
                s = sd - 0.9 * od
                # Small tie-break to prefer nearer resources when similar.
                s += 0.01 * (rx + 10 * ry)
                score = s if score is None else (score if score < s else s)
            # Mildly prefer moves that don't drift away from current position.
            score += 0.02 * (abs(nx - sx) + abs(ny - sy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]