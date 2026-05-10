def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def score_pos(px, py):
        best = None
        best_myd = 10**9
        best_rx = best_ry = None
        for rx, ry in resources:
            myd = cheb(px, py, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we are earlier; otherwise pick nearest but avoid losing races.
            advantage = opd - myd  # positive means we arrive no later
            # Encourage finishing quickly and also reduce opponent ability.
            v = advantage * 20 - myd * 2
            if v > (best if best is not None else -10**18) or (v == best and myd < best_myd):
                best = v
                best_myd = myd
                best_rx, best_ry = rx, ry
        # Second-order: slight pull toward the chosen resource to commit deterministically.
        if best_rx is None:
            return -10**18
        commit = -cheb(px, py, best_rx, best_ry)
        # If we can potentially capture immediately, prioritize it.
        immediate = 5 if (best_myd == 0) else 0
        return best + commit + immediate

    # If multiple moves are equally good, choose deterministically toward minimal cheb to best target.
    best_move = (0, 0)
    best_val = None
    best_tieb = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = score_pos(nx, ny)
        tieb = cheb(nx, ny, sx, sy)
        if best_val is None or v > best_val or (v == best_val and tieb < best_tieb):
            best_val = v
            best_tieb = tieb
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]