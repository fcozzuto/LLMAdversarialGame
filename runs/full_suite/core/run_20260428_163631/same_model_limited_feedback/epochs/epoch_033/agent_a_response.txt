def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation.get("resources", [])
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Pick target: prefer resources where we're relatively closer than opponent, and not too close to opponent
    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = abs(rx - x) + abs(ry - y)
            od = abs(rx - ox) + abs(ry - oy)
            score = (sd - od) * 100 + sd * 3 + od  # smaller is better
            # If opponent is very close, discourage
            if od <= 2:
                score += 1000 + od * 10
            if best is None or score < best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]
    else:
        # No resources: move toward center while keeping distance from opponent
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Choose best next move toward target, avoiding obstacles and penalizing closeness to opponent
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_to_target = abs(tx - nx) + abs(ty - ny)
        dist_to_opp = abs(ox - nx) + abs(oy - ny)
        # If move would let opponent "trap" (adjacent), penalize strongly
        penalty_opp = 0 if dist_to_opp >= 3 else (300 - dist_to_opp * 50)
        # Prefer moves that reduce target distance; slight preference for increasing separation
        val = dist_to_target * 10 - dist_to_opp + penalty_opp
        # Deterministic tie-breaker: prefer non-negative dx then non-negative dy then staying still
        tie = (dx < 0, dy < 0, dx == 0 and dy == 0)
        if best_val is None or val < best_val or (val == best_val and tie < best_tie):
            best_val = val
            best_tie = tie
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]