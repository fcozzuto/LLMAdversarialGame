def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (x, y) in resources:
        return [0, 0]

    # Pick best target: maximize (opp_dist - self_dist), tie-break toward closer and then stable coordinates.
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(x, y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    # If no resources, move toward center/escape toward safer position deterministically.
    if best_r is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_r

    # Greedy step: prioritize moves that reduce distance to target and avoid obstacles.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles and (nx, ny) not in resources:
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        # Higher is better: keep advantage, reduce distance to target, prefer stepping closer when tied.
        score = (d_to_o - d_to_t, -d_to_t, nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]