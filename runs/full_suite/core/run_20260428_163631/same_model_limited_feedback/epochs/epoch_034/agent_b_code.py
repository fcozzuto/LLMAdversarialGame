def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target resource where we have the best distance advantage over the opponent.
    best = None
    best_score = -10**9
    for r in resources:
        if r in obstacles:
            continue
        myd = dist((sx, sy), r)
        opd = dist((ox, oy), r)
        # Prefer being much closer; lightly prefer closer overall.
        score = (opd - myd) * 10 - myd
        if score > best_score:
            best_score = score
            best = r
    if best is None:
        return [0, 0]
    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (dx, dy) == (0, 0):
                continue
            if inside(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    # If we can stay without harm, occasionally do so when already adjacent to target.
    if len(resources) == 1 and dist((sx, sy), best) <= 1:
        return [0, 0]

    # Choose move that reduces distance to target most; break ties by increasing distance to opponent.
    best_move = None
    best_mscore = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        md = dist((nx, ny), (tx, ty))
        od = dist((nx, ny), (ox, oy))
        mscore = -md * 10 + od
        if mscore > best_mscore:
            best_mscore = mscore
            best_move = (dx, dy)

    if best_move is None:
        # No valid move except staying.
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]