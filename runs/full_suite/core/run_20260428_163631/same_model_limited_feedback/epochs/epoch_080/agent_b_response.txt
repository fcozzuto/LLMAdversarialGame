def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp_move(nx, ny):
        if 0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"] and (nx, ny) not in obstacles:
            return [nx - x, ny - y]
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"]) or (nx, ny) in obstacles:
            continue

        if resources:
            d_self = 10**9
            d_opp = 10**9
            for rx, ry in resources:
                ds = dist((nx, ny), (rx, ry))
                if ds < d_self:
                    d_self = ds
                do = dist((ox, oy), (rx, ry))
                if do < d_opp:
                    d_opp = do

            # Encourage being closer to resources, discourage giving opponent advantage,
            # and small tie-breaker toward moving generally away from opponent if tied.
            score = (-2.5 * d_self) + (1.4 * d_opp) + (0.05 * dist((nx, ny), (ox, oy)))
            # If move lands on a resource, heavily prefer it.
            if (nx, ny) in set(tuple(p) for p in resources):
                score += 10000
        else:
            score = 0.0

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]