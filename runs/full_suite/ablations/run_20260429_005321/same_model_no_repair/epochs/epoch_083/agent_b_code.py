def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    best_move = None
    for dx, dy, nx, ny in legal:
        # For each resource, measure "how much closer I am than opponent"
        # Prefer largest positive advantage; then prefer smaller my distance.
        best_for_this = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            adv = op_d - my_d
            cand = (-(adv), my_d, cheb(nx, ny, ox, oy))  # sort: max adv, min my_d, min separation
            if best_for_this is None or cand < best_for_this:
                best_for_this = cand
        if best_move is None or best_for_this < best_move[0]:
            best_move = (best_for_this, dx, dy)

    return [best_move[1], best_move[2]]