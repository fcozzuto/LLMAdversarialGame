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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        # Drift to center-ish to reduce being swept; deterministic.
        tx = 3 if sx <= 3 else 4 if sx >= 4 else sx
        ty = 3 if sy <= 3 else 4 if sy >= 4 else sy
        best = None
        for dx, dy, nx, ny in legal:
            v = (cheb(nx, ny, tx, ty), cheb(sx, sy, tx, ty), dx, dy)
            if best is None or v < best[0]:
                best = (v, (dx, dy))
        return [int(best[1][0]), int(best[1][1])]

    # Choose the move that maximizes our advantage over opponent in reaching the best target.
    # Also discourage targets on opponent's current row (common "sweep_rows" behavior).
    best_move = None  # (score, dx, dy)
    for dx, dy, nx, ny in legal:
        best_for_move = None  # highest
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)

            # Penalize targets on opponent's row to reduce getting outraced by row sweeps.
            row_pen = 2 if ry == oy else 0
            # Small preference for closer-by paths (lower our_d) when ties.
            adv = (opp_d - our_d) - row_pen
            # Deterministic tie-breaking uses coordinates.
            key = (adv, -our_d, -((rx * 10 + ry)), -(dx * 10 + dy))
            if best_for_move is None or key > best_for_move:
                best_for_move = key

        # Prefer moves that maximize best_for_move.
        score = best_for_move
        if best_move is None or score > best_move[0]:
            best_move = (score, (dx, dy))

    return [int(best_move[1][0]), int(best_move[1][1])]