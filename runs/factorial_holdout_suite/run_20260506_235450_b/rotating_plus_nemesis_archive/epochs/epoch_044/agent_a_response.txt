def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in obstacles_list:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a promising resource based on who is closer (Chebyshev for diagonal movement).
    # Advantage = opp_dist - self_dist; also prefer smaller self_dist as secondary.
    best_adv = -10**9
    best_res = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and (sd < (cheb(sx, sy, best_res[0], best_res[1]) if best_res else 10**9) or
                                                 (sd == (cheb(sx, sy, best_res[0], best_res[1]) if best_res else 10**9) and (rx, ry) < (best_res if best_res else (10**9, 10**9))))):
            best_adv = adv
            best_res = (rx, ry)

    tx, ty = best_res

    # Choose move that maximizes resulting advantage and reduces distance to target.
    def move_value(nx, ny):
        # If we can step onto a resource, heavily prioritize.
        if (nx, ny) in {(r[0], r[1]) for r in resources}:
            return 10**6 + (cheb(ox, oy, nx, ny) - cheb(sx, sy, nx, ny))
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd
        # Secondary: keep closer to target and away from where opponent is nearer (avoid ties).
        return adv * 1000 - sd

    best_moves = []
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = move_value(nx, ny)
        if v > best_val:
            best_val = v
            best_moves = [(dx, dy)]
        elif v == best_val:
            best_moves.append((dx, dy))

    # Deterministic tie-break: smallest (dx,dy) in lexicographic order.
    if not best_moves:
        return [0, 0]
    best_moves.sort()
    return [best_moves[0][0], best_moves[0][1]]