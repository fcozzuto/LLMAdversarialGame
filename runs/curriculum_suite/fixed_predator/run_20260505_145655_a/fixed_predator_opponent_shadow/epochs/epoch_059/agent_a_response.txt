def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def sign(v): return 0 if v == 0 else (1 if v > 0 else -1)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        dx = sign(ox - x); dy = sign(oy - y)
        return [-dx, -dy]

    # Pick a resource where we are relatively closer than opponent, else fall back to nearest with opponent consideration.
    best = None
    for rx, ry in resources:
        my_d = abs(rx - x) + abs(ry - y)
        opp_d = abs(rx - ox) + abs(ry - oy)
        adv = opp_d - my_d
        # Favor decisive leads; otherwise prefer minimizing (my_d - 0.5*adv) and then smaller my_d.
        key = (-(adv * 4 + (-my_d)), my_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), my_d, opp_d)
    (rx, ry) = best[1]

    # Local move selection: avoid obstacles, move to reduce distance to chosen target.
    best_move = (10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        d = abs(rx - nx) + abs(ry - ny)
        # If opponent is much closer to target than us, add mild pressure toward cutting distance gap.
        my_after = d
        opp_after = abs(rx - ox - sign(ox - rx)) + abs(ry - oy - sign(oy - ry))  # opponent proxy move
        gap_term = max(0, opp_after - my_after)
        score = (d * 10 + gap_term * 3, abs(dx) + abs(dy), dx, dy)
        if score < best_move:
            best_move = score

    # If all moves blocked, stay put.
    if best_move[2] == 0 and best_move[3] == 0 and (x, y) in obstacles:
        return [0, 0]
    return [best_move[2], best_move[3]]