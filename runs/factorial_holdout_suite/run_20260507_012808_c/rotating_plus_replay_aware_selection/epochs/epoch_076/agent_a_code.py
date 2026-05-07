def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step(posx, posy, tx, ty):
        dx = 0 if tx == posx else (1 if tx > posx else -1)
        dy = 0 if ty == posy else (1 if ty > posy else -1)
        nx, ny = posx + dx, posy + dy
        return (nx, ny) if valid(nx, ny) else (posx, posy)

    def cheb(x1, y1, x2, y2):
        return max(abs(x2-x1), abs(y2-y1))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            key = (d, nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    resources = [tuple(r) for r in resources]
    best_move = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Opponent-deny approximation: opponent moves 1 step toward the same resource.
        best_est = None
        for rx, ry in resources:
            opp_nx, opp_ny = step(ox, oy, rx, ry)
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(opp_nx, opp_ny, rx, ry)
            # Prefer moves that create advantage; if equal, prefer closer self.
            est_adv = opp_d - self_d
            key = (est_adv, -self_d, -cheb(nx, ny, ox, oy))
            if best_est is None or key > best_est[0]:
                best_est = (key, self_d, (rx, ry))
        est_key, self_d, _ = best_est

        # Global tie-break: favor closer to some resource and away from obstacles via stability.
        near_any = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        key = (est_key[0], est_key[1], est_key[2], -near_any, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]