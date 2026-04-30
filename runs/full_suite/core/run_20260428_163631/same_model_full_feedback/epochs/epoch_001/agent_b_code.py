def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx = sx + (-1 if ox > sx else (1 if ox < sx else 0))
        ty = sy + (-1 if oy > sy else (1 if oy < sy else 0))
        tx = 0 if tx < 0 else (w - 1 if tx >= w else tx)
        ty = 0 if ty < 0 else (h - 1 if ty >= h else ty)
        best = (0, 0); bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            v = -dist((nx, ny), (tx, ty))
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    best_res = None
    best_score = -10**18
    for r in resources:
        rx, ry = r
        myd = dist((sx, sy), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        score = (opd - myd) * 1000 - myd
        if score > best_score:
            best_score = score
            best_res = (rx, ry)

    rx, ry = best_res
    target = (rx, ry)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        myd = dist((nx, ny), target)
        opd = dist((ox, oy), target)
        val = (opd - myd) * 1000 - myd
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move