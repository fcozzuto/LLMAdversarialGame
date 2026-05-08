def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx >= dy else dy

    valid_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                valid_moves.append([dx, dy])

    best_move = [0, 0]
    if not resources:
        return best_move

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return best_move

    # Score resources by expected "reach first" advantage, using chebyshev distance (diagonals allowed).
    def resource_score(rx, ry, px, py):
        sd = cheb((px, py), (rx, ry))
        od = cheb((ox, oy), (rx, ry))
        return (od - sd) * 10 - sd

    # Pick move that maximizes our best reachable resource after this step.
    best_val = None
    for dx, dy in valid_moves:
        px, py = sx + dx, sy + dy
        # If we'd collect immediately, strongly prefer it.
        immediate = 1
        val_best = None
        for rx, ry in res:
            s = resource_score(rx, ry, px, py)
            if (rx, ry) == (px, py):
                s += 1000
                immediate = 0
            if val_best is None or s > val_best:
                val_best = s
        val = (immediate, val_best)
        if best_val is None or val[1] > best_val[1] or (val[1] == best_val[1] and val[0] < best_val[0]):
            best_val = val
            best_move = [dx, dy]

    return best_move