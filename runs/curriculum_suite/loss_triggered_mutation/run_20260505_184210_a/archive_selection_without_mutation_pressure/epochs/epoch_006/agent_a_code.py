def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    # Prefer moves that create the largest "steal margin" (opponent distance - our distance)
    # while also progressing toward the best target. Add a small bias to avoid moving into corners
    # that often trap against edge patrol paths.
    best = None
    best_move = (0, 0)

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_steal = -10**9
        best_ds = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            steal = do - ds
            if steal > best_steal or (steal == best_steal and ds < best_ds):
                best_steal = steal
                best_ds = ds

        # Corner avoidance bias (deterministic). Corners can be okay, but edge patrol tends to pressure them.
        corner = 0
        if (nx == 0 or nx == w - 1) and (ny == 0 or ny == h - 1):
            corner = 1

        score = best_steal * 100 - best_ds - 3 * corner
        if best is None or score > best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]