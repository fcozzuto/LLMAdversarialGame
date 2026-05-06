def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (x, y))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(obstacles) if obstacles else set()

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best = None
    best_score = -10**18
    if resources:
        for rx, ry in resources:
            ds = dist(x, y, rx, ry)
            do = dist(ox, oy, rx, ry)
            score = (do - ds) * 100 - ds  # deny high first, then be closer
            if score > best_score:
                best_score = score
                best = (rx, ry)

    if best is None:
        for rx, ry in resources[:1]:
            best = (rx, ry)

    # If still none, just stay or move away from opponent
    if best is None:
        best_move = [0, 0]
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            s = dist(nx, ny, ox, oy)
            if s > dist(x, y, ox, oy):
                best_move = [dx, dy]
                break
        return best_move

    tx, ty = best
    cur_ds = dist(x, y, tx, ty)
    # Choose move that reduces distance to target; tie-break: increases distance from opponent
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        nds = dist(nx, ny, tx, ty)
        ndo = dist(nx, ny, ox, oy)
        val = (cur_ds - nds) * 1000 + ndo - nds
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return [best_move[0], best_move[1]]