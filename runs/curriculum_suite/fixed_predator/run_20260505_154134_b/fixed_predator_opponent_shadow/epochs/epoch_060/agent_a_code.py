def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_towards(px, py, tx, ty):
        dx = 0 if tx == px else (1 if tx > px else -1)
        dy = 0 if ty == py else (1 if ty > py else -1)
        nx, ny = px + dx, py + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            return px, py
        return nx, ny

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_key = None

    if not resources:
        return [0, 0]

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
            penalty = 1
        else:
            penalty = 0

        # Choose move that creates the largest "after one step" advantage over opponent on some resource.
        local_best = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            pnx, pny = step_towards(ox, oy, rx, ry)
            opp_d = cheb(pnx, pny, rx, ry)
            # Primary: maximize opp_d - my_d (how much closer we are than opponent after their next step)
            # Secondary: reduce my_d to secure pickups
            # Tertiary: deterministic tie-break by coordinates
            key = (opp_d - my_d, -my_d, -rx, -ry)
            if local_best is None or key > local_best:
                local_best = key

        final_key = (local_best[0], local_best[1], -penalty, local_best[2], local_best[3])
        if best_key is None or final_key > best_key:
            best_key = final_key
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]