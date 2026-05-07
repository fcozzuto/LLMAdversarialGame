def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        our_best = 10**9
        lead_best = -10**9
        target_closer = (nx, ny)

        for rx, ry in resources:
            d_me = dist(nx, ny, rx, ry)
            d_op = dist(ox, oy, rx, ry)
            if d_me < our_best:
                our_best = d_me
            lead = d_op - d_me
            if lead > lead_best:
                lead_best = lead
                target_closer = (rx, ry)

        # Prefer moves that create a positive lead; tie-break by bigger lead, then smaller own distance.
        # Small bias toward staying closer to "some" resource.
        val = (lead_best * 1000) - (our_best * 5)
        # If no positive lead exists, still pick the closest resource.
        if lead_best <= 0:
            val = (-our_best * 10) + (lead_best * 50)
        # Secondary deterministic tie-break: prefer moves that go toward the selected target coordinates.
        rx, ry = target_closer
        to_t = dist(nx, ny, rx, ry)
        val -= to_t * 0.1

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]