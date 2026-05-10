def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = [tuple(r) for r in observation.get("resources", []) if 0 <= r[0] < w and 0 <= r[1] < h and tuple(r) not in obstacles]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # One-step lookahead: pick the move that maximizes our best "race advantage"
    # advantage for a resource = 3*(opp_dist - self_dist) - self_dist
    # (so we strongly prefer resources where we are closer than opponent, else still prefer smaller self_dist)
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # If we reach any resource immediately, take it deterministically (no need to compare further)
        if (nx, ny) in resources:
            return [dx, dy]

        local_best = None
        for rx, ry in resources:
            dm = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = 3 * (do - dm) - dm
            # Slight tie-break: prefer smaller distance-to-resource among equally advantaged states
            key = (-(adv), dm, rx, ry)
            if local_best is None or key < local_best:
                local_best = key

        # Convert local_best back to a comparable score tuple for moves
        # local_best is (-adv as positive) so smaller key[0] means larger adv
        move_key = (local_best[0], local_best[1], abs(nx - ox) + abs(ny - oy), nx, ny)
        if best_score is None or move_key < best_score:
            best_score = move_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]