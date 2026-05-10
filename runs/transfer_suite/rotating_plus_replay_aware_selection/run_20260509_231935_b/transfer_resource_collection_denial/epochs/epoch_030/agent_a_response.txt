def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    res_set = set(tuple(p) for p in resources)

    opp_to = {}
    for rx, ry in resources:
        opp_to[(rx, ry)] = dist8(ox, oy, rx, ry)

    # If we can collect a resource immediately, do so deterministically.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) in res_set:
            if (nx, ny) not in obstacles:
                return [dx, dy]

    best_val = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0.0
        # Prefer resources where we are closer than opponent, and generally closer overall.
        for rx, ry in resources:
            d_our = dist8(nx, ny, rx, ry)
            d_opp = opp_to[(rx, ry)]
            # Higher is better: immediate closeness + relative advantage.
            val += 50.0 / (1 + d_our) + 10.0 * (d_opp - d_our)

        # Small penalty for moving away from the opponent's likely race: keep pressure near closest contested resource.
        if resources:
            # contested distance difference for the nearest resource from our candidate
            mind = None
            for rx, ry in resources:
                d_our = dist8(nx, ny, rx, ry)
                if mind is None or d_our < mind[0]:
                    mind = (d_our, opp_to[(rx, ry)] - d_our)
            if mind is not None:
                val += 5.0 * mind[1]

        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move