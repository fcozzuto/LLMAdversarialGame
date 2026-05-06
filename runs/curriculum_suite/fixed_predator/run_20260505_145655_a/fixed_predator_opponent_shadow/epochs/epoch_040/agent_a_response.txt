def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Choose a deterministic target: prefer resources where we are closer than the opponent,
    # but still react if we are generally behind.
    best = None
    bestv = -10**18
    for tx, ty in resources:
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        v = (d_opp - d_me) * 120 - d_me + (d_opp * 0.05)
        if v > bestv:
            bestv = v
            best = (tx, ty)
        elif v == bestv and best is not None:
            if d_me < (abs(best[0] - x) + abs(best[1] - y)):
                best = (tx, ty)

    tx, ty = best
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Move selection with obstacle avoidance and slight distancing from the opponent.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if blocked(nx, ny):
            continue
        d_next_target = abs(tx - nx) + abs(ty - ny)
        d_next_opp = abs(ox - nx) + abs(oy - ny)
        d_cur_target = abs(tx - x) + abs(ty - y)
        # primary: minimize distance to target; secondary: keep opponent farther when contesting.
        contest = bestv < 0
        score = (-d_next_target) * 100 + d_next_opp * (3 if contest else 1) - (d_cur_target - d_next_target) * 2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves blocked (rare), stay.
    return [best_move[0], best_move[1]]