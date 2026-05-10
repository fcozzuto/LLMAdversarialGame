def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        tx, ty = w - 1, h - 1
        return [0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1)]

    best_val = -10**18
    best_move = [0, 0]
    opp_min = min(dist8(ox, oy, rx, ry) for rx, ry in resources)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate by how much closer we become to the best contested resource.
        best_diff = -10**18
        best_tie = 10**18
        for rx, ry in resources:
            our_d = dist8(nx, ny, rx, ry)
            opp_d = dist8(ox, oy, rx, ry)
            diff = opp_d - our_d
            if diff > best_diff or (diff == best_diff and our_d < best_tie):
                best_diff = diff
                best_tie = our_d

        # Prefer shortening our distance to resources slightly, and reacting when we're behind.
        val = best_diff * 1000 - best_tie
        if best_diff <= 0:
            val -= (opp_min - min(dist8(ox, oy, rx, ry) for rx, ry in resources)) * 10

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move