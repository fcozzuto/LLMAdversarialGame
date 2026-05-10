def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist8(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w - 1, h - 1
        if sx < w // 2:
            tx = w // 2
        elif sx > w // 2:
            tx = 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)]

    best_val = -10**18
    best_move = [0, 0]

    # Precompute opponent distances to each resource
    opp_d = []
    for rx, ry in resources:
        opp_d.append((rx, ry, dist8(ox, oy, rx, ry)))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0.0
        # Prefer positions that let us beat opponent to some resource.
        for rx, ry, od in opp_d:
            d = dist8(nx, ny, rx, ry)
            # Large bonus if we land on a resource now.
            on = 1 if (nx == rx and ny == ry) else 0
            # Beat measure: opponent - ours (positive means we are closer or equal).
            beat = od - d
            # Weight beating more than raw progress.
            val += (beat * 10.0 + on * 200.0) - d * 0.35
        # Also slightly prefer smaller distance to the single best resource.
        best_single = 10**9
        for rx, ry, od in opp_d:
            d = dist8(nx, ny, rx, ry)
            score = (od - d, -d)
            # Convert to deterministic scalar using lexicographic preferences
            # (higher beat, then smaller d).
            pass
        for rx, ry, od in opp_d:
            d = dist8(nx, ny, rx, ry)
            beat = od - d
            if beat > 0 or (beat == 0 and d < best_single):
                best_single = d
        val += (14.0 - best_single) * 0.5

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [best_move[0], best_move[1]]