def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def passable(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w // 2, h // 2)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if passable(sx + dx, sy + dy):
            return [dx, dy]
        # fallback: any passable move toward center-ish
        best = [0, 0]
        bestv = -10**9
        for ddx, ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if not passable(nx, ny):
                continue
            v = -(cheb(nx, ny, tx, ty))
            if v > bestv or (v == bestv and (ddx, ddy) < tuple(best)):
                bestv = v
                best = [ddx, ddy]
        return best

    best_move = [0, 0]
    best_val = -10**18

    # Choose the move that maximizes advantage on the best contestable resource.
    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not passable(nx, ny):
            continue

        move_val = -cheb(nx, ny, w // 2, h // 2) * 0.01  # tiny center bias

        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            if our_d == 0 and opp_d == 0:
                continue
            # Strongly prefer becoming closer than opponent to reachable resources.
            advantage = opp_d - our_d
            # Also prefer resources that are near overall (faster claim).
            urgency = 7 - our_d
            # Discourage allowing opponent to be significantly closer.
            allow_pen = 0
            if advantage < 0:
                allow_pen = (-advantage) * 6

            # Deterministic tie-break inputs.
            key = (rx * 31 + ry * 17) % 97
            score = advantage * 100 + urgency * 3 - allow_pen + (key * 0.001)
            if score > move_val:
                move_val = score

        # Deterministic tie-break: prefer staying only if equal, else fixed order by (ddx,ddy).
        cand = (move_val, -abs(ddx), -abs(ddy), -(ddx + 2 * ddy), ddx, ddy)
        best_cand = (best_val,
                      -abs(best_move[0]), -abs(best_move[1]),
                      -(best_move[0] + 2 * best_move[1]),
                      best_move[0], best_move[1])
        if cand > best_cand:
            best_val = move_val
            best_move = [ddx, ddy]

    # If all candidate moves were blocked, return stay.
    return best_move