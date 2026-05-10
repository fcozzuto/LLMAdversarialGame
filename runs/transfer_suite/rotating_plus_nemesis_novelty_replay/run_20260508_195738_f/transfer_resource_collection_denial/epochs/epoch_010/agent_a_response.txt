def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Fallback: drift toward center away from opponent
    if not resources:
        cx, cy = w // 2, h // 2
        tx = cx if cx != ox else (0 if ox > cx else w - 1)
        ty = cy if cy != oy else (0 if oy > cy else h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        return [0, 0]

    res = [(int(x), int(y)) for x, y in resources]
    best_val = -10**18
    best_move = [0, 0]

    # For each possible next step, pick the resource where we maximize "arrival advantage"
    # over the opponent, then slightly prefer getting closer to the chosen resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Score of the best resource after taking this move.
        local_best = -10**18
        for rx, ry in res:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Primary: how much earlier we can arrive than opponent.
            # Secondary: among equal advantage, prefer shorter self_d.
            # Tertiary: deterministic tie using coordinates.
            adv = opp_d - self_d
            val = (adv * 1000) + (-self_d) + (-(rx + ry) * 1e-6)
            if val > local_best:
                local_best = val

        # Additional penalty: if we step onto a resource, prioritize it (fastest turnaround).
        on_res_bonus = 5 if (nx, ny) in set(res) else 0

        # Also add small penalty for moving away from our current preferred direction:
        # prefer larger reduction in distance to the best-advantage resource (approximated via local_best).
        move_cost = 0.2 if (dx, dy) != (0, 0) else 0.0

        val = local_best + on_res_bonus - move_cost
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move