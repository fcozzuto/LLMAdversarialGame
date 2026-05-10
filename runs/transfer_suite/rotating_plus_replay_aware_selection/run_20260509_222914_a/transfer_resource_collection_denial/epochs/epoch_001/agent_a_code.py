def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    # If no resources, drift toward center to be consistent
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Choose target: nearest resource by Chebyshev distance (diagonal-friendly)
        best = None
        for rx, ry in resources:
            d = max(abs(rx - x), abs(ry - y))
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        tx, ty = best[1]

    # Generate candidate moves (including stay), filter obstacles/bounds
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1,  0), (0,  0), (1,  0),
              (-1,  1), (0,  1), (1,  1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer collecting proximity and slightly discourage moving toward opponent early
        dist = max(abs(tx - nx), abs(ty - ny)) if resources else max(abs(tx - nx), abs(ty - ny))
        opp_dist = max(abs(ox - nx), abs(oy - ny))
        # If on a resource, dist becomes 0 naturally via target selection; still score properly
        score = (dist, -opp_dist, dx, dy)
        candidates.append((score, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort()
    return candidates[0][1]