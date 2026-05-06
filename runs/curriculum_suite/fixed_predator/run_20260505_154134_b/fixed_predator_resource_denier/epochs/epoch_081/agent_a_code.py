def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cx, cy = w // 2, h // 2

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            key = (-cheb(nx, ny, cx, cy), -cheb(nx, ny, ox, oy), -cheb(nx, ny, 0, 0))
            if best is None or key > best[0]:
                best = (key, (dx, dy))
        return list(best[1]) if best else [0, 0]

    best_key = None
    best_move = (0, 0)
    # Deterministic: tie-break by move order in `moves`
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Resource value: prefer cells where we are much closer than opponent (deny)
        best_res_for_move = -10**9
        tie_my_dist = 10**9
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            if my_d == 0:
                val = 10**6 + opp_d  # immediate pickup priority
            else:
                val = (opp_d - my_d) * 100 - my_d  # denier-friendly: biggest lead + shorter
            if val > best_res_for_move or (val == best_res_for_move and my_d < tie_my_dist):
                best_res_for_move = val
                tie_my_dist = my_d

        # Also slightly prefer moves that reduce my distance to the best resource
        # and increase opponent distance to it.
        key = (best_res_for_move, -tie_my_dist, cheb(nx, ny, cx, cy), -(cheb(nx, ny, ox, oy)))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]