def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        if not resources:
            # With no known resources, drift away from opponent while staying safe-ish.
            score = (man(nx, ny, ox, oy)) - 0.01 * (abs(dx) + abs(dy))
        else:
            best_resource_val = -10**18
            for rx, ry in resources:
                myd = man(nx, ny, rx, ry)
                opd = man(ox, oy, rx, ry)
                val = (opd - myd) - 0.05 * myd
                if myd == 0:
                    val += 30
                best_resource_val = val if val > best_resource_val else best_resource_val
            # Small penalty for getting too close to opponent unless it helps capture (covered by advantage).
            score = best_resource_val - 0.01 * max(0, 6 - man(nx, ny, ox, oy))
            # Encourage movement: mild preference for not staying still.
            if dx == 0 and dy == 0:
                score -= 0.02

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move