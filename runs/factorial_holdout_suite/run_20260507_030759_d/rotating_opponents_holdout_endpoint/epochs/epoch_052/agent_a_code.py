def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        best_res = None
        best_score = None
        for rx, ry in resources:
            dself = abs(rx - sx) + abs(ry - sy)
            dopp = abs(rx - ox) + abs(ry - oy)
            score = (dopp - dself) * 10 - dself
            if best_score is None or score > best_score:
                best_score = score
                best_res = (rx, ry)

        rx, ry = best_res
        # Prefer moves that reduce distance to target; tie-break against being closer to opponent.
        best_move = None
        best_val = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d_to_res = abs(rx - nx) + abs(ry - ny)
            d_to_opp = abs(ox - nx) + abs(oy - ny)
            val = (-d_to_res) * 100 + d_to_opp
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No visible resources: drift away from opponent while still moving to unblocked space.
    best_move = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dist_opp = abs(ox - nx) + abs(oy - ny)
        # Slight preference for increasing distance from center direction to reduce collisions.
        dist_center = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        val = dist_opp * 10 + dist_center
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]