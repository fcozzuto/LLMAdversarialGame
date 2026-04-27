def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # race: prioritize resources where we are closer than opponent, then overall advantage
            key = (od - sd, -sd, rx, ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    # Choose move that decreases our distance to target; if close, also avoid giving opponent an edge.
    best_move = None
    best_key = None
    for dx, dy, nx, ny in legal:
        sd = cheb(nx, ny, tx, ty)
        cur_sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        n_od = od  # opponent move unknown; use only current estimate, penalize moves that make target "easier" for opponent in future
        # Prefer moves that reduce our distance; slight tie-break toward increasing separation from opponent.
        sep = cheb(nx, ny, ox, oy)
        key = (-sd, -(cur_sd - sd), sep, dx, dy)
        # If we have already reached target, stabilize (stay) deterministically.
        if (sx, sy) == (tx, ty):
            key = (-sd, -0, sep, 0, 0)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]