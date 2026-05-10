def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    self_role = (observation.get("self_role") or "").lower()
    env = (observation.get("environment_name") or "").lower()
    i_pursuer = ("pursuer" in self_role and "evader" not in self_role) or ("pursuit" in env and "evad" not in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def greedy_pursuer_step(px, py, tx, ty):
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not legal(nx, ny):
                continue
            val = d2(nx, ny, tx, ty)
            if val < best[0]:
                best = (val, dx, dy)
        return best[1], best[2]

    def greedy_evader_step(px, py, tx, ty):
        best = (-1, 0, 0)
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not legal(nx, ny):
                continue
            val = d2(nx, ny, tx, ty)
            if val > best[0]:
                best = (val, dx, dy)
        return best[1], best[2]

    if i_pursuer:
        best_score = -10**18
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            pdx, pdy = greedy_evader_step(ox, oy, nx, ny)
            nox, noy = ox + pdx, oy + pdy
            score = -d2(nx, ny, nox, noy)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        best_score = -10**18
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            pdx, pdy = greedy_pursuer_step(ox, oy, nx, ny)
            nox, noy = ox + pdx, oy + pdy
            score = d2(nx, ny, nox, noy)  # maximize separation after pursuer responds
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]