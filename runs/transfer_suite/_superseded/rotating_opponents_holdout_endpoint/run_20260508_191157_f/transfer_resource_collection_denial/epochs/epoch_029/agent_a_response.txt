def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = set((x, y) for x, y in (observation.get("obstacles") or []))

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = [0, 0]
    best_val = -10**18

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue

            # Evaluate the best resource we could plausibly claim from this neighbor,
            # balancing "reach first" vs "reduce our distance".
            local_best = -10**18
            for rx, ry in resources:
                my_d = dist(nx, ny, rx, ry)
                opp_d = dist(ox, oy, rx, ry)
                # Positive means we're closer than opponent; stronger preference when we lead.
                val = (opp_d - my_d) * 100 - my_d
                # Slightly discourage moving away from any nearby resource.
                val -= 3 * max(0, my_d - dist(sx, sy, rx, ry))
                if val > local_best:
                    local_best = val

            if local_best > best_val:
                best_val = local_best
                best_move = [dx, dy]

    return best_move