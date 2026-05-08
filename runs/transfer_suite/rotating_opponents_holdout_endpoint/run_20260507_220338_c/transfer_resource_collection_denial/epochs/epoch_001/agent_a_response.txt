def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None

    # Deterministic tie-breaking order: closer first, then dx/dy preference.
    pref = {(-1, -1): 0, (-1, 0): 1, (-1, 1): 2, (0, -1): 3, (0, 0): 4, (0, 1): 5, (1, -1): 6, (1, 0): 7, (1, 1): 8}
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # match engine behavior (invalid -> stay)
        # Choose best resource target given this move.
        # Prefer resources where we become/are closer than opponent.
        best_score = None
        for rx, ry in resources:
            sdist = dist((nx, ny), (rx, ry))
            odist = dist((ox, oy), (rx, ry))
            # Score: lower is better. Add bias to prioritize contested resources we can beat.
            score = (sdist - odist) * 100 + sdist
            if best_score is None or score < best_score:
                best_score = score
        if best is None or best_score < best[0] or (best_score == best[0] and pref[(dx, dy)] < pref[best[2]]):
            best = (best_score, (nx, ny), (dx, dy))

    return [best[2][0], best[2][1]]