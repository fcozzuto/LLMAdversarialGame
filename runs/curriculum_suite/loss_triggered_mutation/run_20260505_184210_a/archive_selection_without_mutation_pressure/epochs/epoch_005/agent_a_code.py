def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 1))
    h = int(observation.get("grid_height", 1))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

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

    if resources:
        best_score = None
        best_move = (0, 0)
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            score = 10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Prefer positions where we are closer than opponent (steal); otherwise deny by minimizing opp advantage.
                s = myd - opd
                if s < score:
                    score = s
            # Tie-break: also prefer staying closer to some resource.
            score2 = score + 0.01 * cheb(nx, ny, resources[0][0], resources[0][1])
            if best_score is None or score2 < best_score:
                best_score = score2
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move to reduce distance to opponent's corner (deterministic pressure).
    tx, ty = w - 1, h - 1
    best_score = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        score = cheb(nx, ny, tx, ty)
        if best_score is None or score < best_score or (score == best_score and (nx + ny) < (sx + sy)):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]