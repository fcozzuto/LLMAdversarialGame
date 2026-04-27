def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_dist2(px, py, res_list):
        best = None
        for rx, ry in res_list:
            dx, dy = rx - px, ry - py
            d2 = dx * dx + dy * dy
            if best is None or d2 < best:
                best = d2
        return best if best is not None else 10**18

    # If no resources, drift toward opponent to force interaction.
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    # If standing on a resource, stay (collection assumed by engine).
    if any((sx, sy) == tuple(r) for r in resources):
        return [0, 0]

    # Candidate move evaluation: choose move that targets a resource where we gain the most distance advantage.
    best_move = (0, 0)
    best_score = -10**18
    best_self_d2 = 10**18

    # Precompute opponent "greedy nearest resource" distance for advantage.
    # For each candidate resource, compare our distance vs opponent's distance to that same resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Compute our best target resource where opponent is relatively far.
        self_best_d2 = 10**18
        opp_best_d2 = 10**18
        gain_best = -10**18

        for rx, ry in resources:
            sd = nx - rx
            sy2 = ny - ry
            sd2 = sd * sd + sy2 * sy2
            od = ox - rx
            oy2 = oy - ry
            od2 = od * od + oy2 * oy2
            # Prefer resources where opponent is farther; tie-break toward nearer for us.
            gain = od2 - sd2
            if gain > gain_best or (gain == gain_best and sd2 < self_best_d2):
                gain_best = gain
                self_best_d2 = sd2
                opp_best_d2 = od2

        # Also incorporate mild pressure: if we can get closer than opponent overall to any resource, reward it.
        our_min_any = nearest_dist2(nx, ny, resources)
        opp_min_any = nearest_dist2(ox, oy, resources)
        score = gain_best + 0.15 * (opp_min_any - our_min_any)

        if score > best_score or (score == best_score and self_best_d2 < best_self_d2):
            best_score = score
            best_self_d2 = self_best_d2
            best_move = (dx, dy)

    # If all moves were blocked, stay.
    return [best_move[0], best_move[1]]