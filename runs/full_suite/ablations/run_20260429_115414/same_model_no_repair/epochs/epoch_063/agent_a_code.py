def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def cd(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    # One-step reach approximation: in Chebyshev metric, a move reduces distance by at most 1
    def next_dist(curx, cury, tx, ty):
        d = cd(curx, cury, tx, ty)
        d1 = d - 1
        return 0 if d1 < 0 else d1

    best_move = (0, 0)
    best_val = None

    # Prefer a resource we can contest while strongly denying resources where opponent is closer.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        worst = None
        for rx, ry in resources:
            our_nd = next_dist(nx, ny, rx, ry)
            opp_nd = next_dist(ox, oy, rx, ry)  # opponent hasn't moved yet
            margin = opp_nd - our_nd  # positive means we are closer than opponent after both can move once

            # If opponent can capture immediately (<=1 now), we should not ignore that resource.
            opp_can_now = 1 if cd(ox, oy, rx, ry) <= 1 else 0
            our_can_now = 1 if cd(nx, ny, rx, ry) <= 0 else 0  # if on resource now

            # Weight: contesting matters more than distant gains; prioritize immediate contest/capture.
            local = 1.8 * margin + 6.0 * our_can_now - 4.5 * opp_can_now
            if worst is None or local < worst:
                worst = local
            val += local

        # Use worst-case contest pressure as primary, total as tie-break.
        key = (worst, val, -(nx - sx) * (nx - sx) - (ny - sy) * (ny - sy), nx, ny)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]