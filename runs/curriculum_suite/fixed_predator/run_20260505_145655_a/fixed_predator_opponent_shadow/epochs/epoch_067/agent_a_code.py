def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def move_score(nx, ny, tx, ty):
        if (nx, ny) in obstacles:
            return -10**9
        my_d = man(nx, ny, tx, ty)
        opp_d = man(nx, ny, ox, oy)
        # Prefer approaching chosen resource while increasing separation from opponent
        return -my_d * 10 + opp_d * 1

    if not resources:
        dx = -sign(ox - x)
        dy = -sign(oy - y)
        return [dx, dy]

    # Pick a target resource where we are relatively closer than the opponent
    best = resources[0]
    best_val = None
    for r in resources:
        tx, ty = r[0], r[1]
        my_d = man(x, y, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        # Value: prioritize positive lead (opponent farther), break ties by smaller my_d
        val = (opp_d - my_d) * 1000 - my_d
        if best_val is None or val > best_val or (val == best_val and (my_d < man(x, y, best[0], best[1]) or (my_d == man(x, y, best[0], best[1]) and (tx, ty) < (best[0], best[1])))):
            best_val = val
            best = r

    tx, ty = best[0], best[1]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_ms = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        ms = move_score(nx, ny, tx, ty)
        if best_ms is None or ms > best_ms or (ms == best_ms and (abs(dx) + abs(dy), dx, dy) < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1])):
            best_ms = ms
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]