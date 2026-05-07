def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy
    def neighbors_legal(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if legal(nx, ny):
                c += 1
        return c

    my_on_resource = (sx, sy) in set((r[0], r[1]) for r in resources)
    if my_on_resource:
        return [0, 0]

    if resources:
        best_r = None
        best_adv = -10**9
        for r in resources:
            rx, ry = r
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = (od - md)  # positive means I'm closer (faster denial race)
            # Prefer resources I can reach sooner; break ties toward larger distance-to-opponent (less likely contested)
            key = (adv, -od, -md)
            if best_r is None or key > best_r:
                best_r = key
                best_xy = (rx, ry)
        tx, ty = best_xy
    else:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2

    best_move = [0, 0]
    best_score = -10**18
    my_res_set = set((r[0], r[1]) for r in resources)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist_t = cheb(nx, ny, tx, ty)
        dist_o = cheb(nx, ny, ox, oy)
        nfree = neighbors_legal(nx, ny)
        on_res = 1.0 if (nx, ny) in my_res_set else 0.0
        # If staying still helps secure current target, keep slight bias.
        stay_bias = 0.02 if (dx == 0 and dy == 0) else 0.0
        # Penalize approaching opponent too closely (resource_denier often lurks to contest)
        opp_pen = 0.0
        if dist_o <= 1:
            opp_pen = 50.0
        elif dist_o == 2:
            opp_pen = 8.0
        # Total: prioritize immediate collection, then reduce distance to target, keep mobility, and manage opponent proximity.
        score = 200.0 * on_res - 3.0 * dist_t + 0.15 * nfree - opp_pen + stay_bias
        # Deterministic tie-break: prefer diagonal, then cardinal, then smaller dx/dy magnitude, then lexicographic
        if score > best_score or (score == best_score and (abs(dx)+abs(dy), dx, dy) < (abs(best_move[0])+abs(best_move[1]), best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]