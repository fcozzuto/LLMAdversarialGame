def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obstacle_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacle_set

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        dx = -dx if dx < 0 else dx
        dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources where we're more likely to secure first; then closer.
        key = (od - myd, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best_mv = (0, 0)
    best_score = None
    # Greedy: move to reduce our distance to target, and avoid positions that let opponent get much closer.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = cheb(nx, ny, rx, ry)
        od2 = cheb(ox, oy, rx, ry)
        # Opponent-relative pressure (lower is better for us).
        score = (myd2, -(od2 - myd2), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]