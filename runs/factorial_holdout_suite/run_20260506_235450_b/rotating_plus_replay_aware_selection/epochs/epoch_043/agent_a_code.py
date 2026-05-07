def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best_moves = []
    best_score = None

    if not resources:
        return [0, 0]

    # Prefer a move that improves the "race" to some resource.
    # Strategy: among legal moves, choose the one maximizing (opp_time - self_time),
    # with tie-breakers for smaller self_time and reaching exact landing on a resource.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Compute score based on best resource from next position.
        move_best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # win_margin: positive means we are closer/equal than opponent
            win_margin = do - ds
            on_resource = 1 if (nx == rx and ny == ry) else 0
            # sweep_rows opponent tends to pressure rows; slight bias to reduce row/col distance too
            rowcol = abs(nx - rx) + abs(ny - ry)
            score_tuple = (win_margin, on_resource, -ds, -rowcol)
            if move_best is None or score_tuple > move_best:
                move_best = score_tuple
        if move_best is None:
            continue
        if best_score is None or move_best > best_score:
            best_score = move_best
            best_moves = [(dx, dy)]
        elif move_best == best_score:
            best_moves.append((dx, dy))

    if not best_moves:
        return [0, 0]

    # Deterministic tie-break: choose move with smallest lexicographic order (dx,dy).
    best_moves.sort()
    dx, dy = best_moves[0]
    return [dx, dy]