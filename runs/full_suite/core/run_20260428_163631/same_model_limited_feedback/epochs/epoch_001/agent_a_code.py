def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for 8-neighbor

    def score_next(nx, ny, target):
        d_after = dist((nx, ny), target)
        d_opp = dist((nx, ny), (ox, oy))
        # Prefer reducing distance to target, and slightly prefer staying away from opponent.
        return d_after * 10 - d_opp

    # If no resources, retreat/avoid opponent deterministically: maximize distance from opponent.
    if not resources:
        best = None
        best_s = None
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                continue
            s = dist((nx, ny), (ox, oy))
            if best_s is None or s > best_s or (s == best_s and (dx, dy) < best):
                best_s, best = s, (dx, dy)
        return list(best if best is not None else (0, 0))

    # Choose the resource where we are "most competitive": closest to us, with a tiebreaker vs opponent.
    best_target = None
    best_t = None
    for r in resources:
        d_self = dist((x, y), r)
        d_opp = dist((ox, oy), r)
        # Prefer smaller self distance, then larger gap (opponent farther).
        t = (d_self, -(d_opp - d_self))
        if best_t is None or t < best_t:
            best_t, best_target = t, tuple(r)

    # Move toward the chosen target while avoiding obstacles.
    best_move = None
    best_s = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or ny < 0 or nx >= observation["grid_width"] or ny >= observation["grid_height"]:
            continue
        if (nx, ny) in obstacles:
            continue
        s = score_next(nx, ny, best_target)
        if best_s is None or s < best_s or (s == best_s and (dx, dy) < best_move):
            best_s, best_move = s, (dx, dy)

    # If all moves blocked, stay.
    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]