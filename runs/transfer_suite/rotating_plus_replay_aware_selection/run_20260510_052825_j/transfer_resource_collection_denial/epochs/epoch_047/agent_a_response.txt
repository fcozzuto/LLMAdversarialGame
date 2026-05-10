def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    valid = []
    for p in resources:
        x, y = p[0], p[1]
        if inb(x, y) and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    best = None
    for rx, ry in valid:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Strongly prefer resources we can secure; otherwise prefer ones where we are less behind.
        # Tie-break: prefer smaller sd then smaller (sd-od).
        score = (0 if sd < od else 1, (sd - od), sd, rx, ry)
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    cur_sd = cheb(sx, sy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        # If we can't reduce distance, still allow staying if it blocks opponent path via proximity penalty.
        n_opp_to_target = cheb(ox, oy, tx, ty)
        # Penalize moves that bring us closer to the target only slightly when opponent is already closer.
        penalty = 0
        if cur_sd >= cheb(ox, oy, tx, ty) and nsd >= cur_sd:
            penalty = 2
        key = (nsd, 0 if nsd < cur_sd else 1, penalty, abs(ox - nx) + abs(oy - ny), dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, (dx, dy))

    if best_move is None:
        return [0, 0]
    return [best_move[1][0], best_move[1][1]]