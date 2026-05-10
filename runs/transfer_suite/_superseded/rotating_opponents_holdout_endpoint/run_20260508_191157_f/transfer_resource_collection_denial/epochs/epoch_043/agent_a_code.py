def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obs_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Pick a target that we can reach earlier (larger opp-self advantage); tie-break by being closer.
    best_t = None
    best_k = None
    for rx, ry in resources:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        k = (od - sd, -sd, -rx, -ry)
        if best_k is None or k > best_k:
            best_k = k
            best_t = (rx, ry)
    tx, ty = best_t

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Also lightly bias toward cells that reduce distance to the next-closest resource.
    other_min = min((manh(sx, sy, rx, ry) for rx, ry in resources if (rx, ry) != (tx, ty)), default=10**9)

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        self_to_t = manh(nx, ny, tx, ty)
        opp_to_t = manh(ox, oy, tx, ty)  # opponent doesn't move this turn
        lead = opp_to_t - self_to_t  # higher is better

        # Greedy attention to next resource to avoid oscillation
        nd_other = other_min
        if len(resources) > 1:
            nd_other = min(manh(nx, ny, rx, ry) for rx, ry in resources if (rx, ry) != (tx, ty))

        key = (lead, -self_to_t, -(nd_other), -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]