def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def cell_free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Choose best target resource deterministically: maximize our advantage, then closeness.
    best = None
    best_score = None
    for r in resources:
        tx, ty = r[0], r[1]
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead = d_opp - d_me
        # Strongly prefer cells where we are closer; break ties toward those opponent is far from.
        s = lead * 1000 - d_me + d_opp * 0.001 + (-(tx + ty) * 0.000001)
        if best_score is None or s > best_score:
            best_score = s
            best = (tx, ty)

    tx, ty = best
    # Evaluate next step toward target, with a penalty for moving away, obstacle avoidance, and for helping opponent.
    best_move = (0, 0)
    best_move_score = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not cell_free(nx, ny):
            continue
        d_me = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # Move should reduce our distance to target and increase our relative advantage.
        s = (d_opp - d_me) * 1000 - d_me
        # Encourage progress in the correct direction.
        s += -(abs(tx - x) + abs(ty - y) - (abs(tx - nx) + abs(ty - ny))) * 2
        # Discourage letting opponent reach much sooner to the target.
        s -= (d_opp - (abs(tx - nx) + abs(ty - ny))) < 0 and 50 or 0
        if best_move_score is None or s > best_move_score:
            best_move_score = s
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]