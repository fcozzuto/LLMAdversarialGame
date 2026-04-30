def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    # Determine candidate target: best resource by Chebyshev distance difference (closer to us relative to opponent)
    target = None
    best_score = -10**9
    for rx, ry in resources:
        d_me = cheb((mx, my), (rx, ry))
        d_op = cheb((ox, oy), (rx, ry))
        score = d_op - d_me  # prefer resources closer to me and far from opponent
        if score > best_score:
            best_score = score
            target = (rx, ry)

    if target is not None:
        tx, ty = target
        # choose move that reduces distance to target while staying legal
        best_move = (0, 0)
        best_dist = 10**9
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not legal(nx, ny):
                continue
            dist = cheb((nx, ny), target)
            if dist < best_dist:
                best_dist = dist
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resource worth pursuing: move towards center area away from opponent, deterministically
    center_x = w // 2
    center_y = h // 2
    target = (center_x, center_y)

    best_move = (0, 0)
    best_score = 10**9
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not legal(nx, ny):
            continue
        # Prefer moves that increase distance from opponent if currently closer
        dist_to_center = cheb((nx, ny), target)
        dist_op = cheb((ox, oy), (nx, ny))
        score = dist_to_center + dist_op * 0  # deterministic tie-breaker only by dist_to_center
        if score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]