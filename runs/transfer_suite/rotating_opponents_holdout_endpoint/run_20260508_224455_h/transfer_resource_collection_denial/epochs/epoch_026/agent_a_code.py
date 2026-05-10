def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonals allowed)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_penalty(x, y):
        pen = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if inb(nx, ny) and (nx, ny) in obstacles:
                    pen += 1
        return pen

    best = None  # (key tuple, target)
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer resources where we are not behind; then closeness; then obstacle-safety; deterministic coord tie.
        behind = sd - od  # <=0 means we are ahead or tied
        key = (behind, sd, cell_penalty(rx, ry), ry, rx)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    (rx, ry) = best[1]

    dx = rx - sx
    dy = ry - sy
    step_options = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Prefer moves that reduce Chebyshev distance to target; break ties by safety and deterministic ordering.
    best_move = None
    best_key = None
    for mdx, mdy in step_options:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue
        nd = dist(nx, ny, rx, ry)
        mdist = dist(sx, sy, rx, ry)
        progress = mdist - nd
        key = (-progress, cell_penalty(nx, ny), ny, nx)  # progress first, then safety
        if best_key is None or key < best_key:
            best_key = key
            best_move = [mdx, mdy]

    return best_move if best_move is not None else [0, 0]