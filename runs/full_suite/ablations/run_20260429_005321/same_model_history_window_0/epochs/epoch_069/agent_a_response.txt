def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev for diagonal moves

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a resource we are relatively closer to than the opponent
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = dist((sx, sy), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            # Prefer positive advantage; also break ties by smaller my distance then lexicographic
            key = (-(opd - myd), myd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No visible resources: move to center while avoiding opponent
        tx, ty = (w // 2, h // 2)

    # Choose next step that best advances toward target and keeps away from opponent
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_next = dist((nx, ny), (tx, ty))
        opp_next = dist((nx, ny), (ox, oy))
        # Score: prioritize reducing distance to target; then maximize distance from opponent; then deterministic tie-break
        score = (my_next, -opp_next, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]