def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick target: prefer resources we can reach sooner (vs opponent), with tie-break by position.
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        us = d_cheb(sx, sy, rx, ry)
        op = d_cheb(ox, oy, rx, ry)
        # maximize advantage => minimize (op - us) and (us) with deterministic tie-break
        key = (-(op - us), us, rx * 8 + ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    if best_t is None:
        best_t = tuple(resources[0])
    tx, ty = best_t

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_mv = (0, 0)
    best_sc = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        our_d = d_cheb(nx, ny, tx, ty)
        opp_d = d_cheb(ox, oy, tx, ty)
        # Evaluate "race": how much closer we are than opponent (if opponent were moving optimally)
        # and keep away from opponent to reduce contest.
        race = our_d - opp_d

        # Additional block: penalize stepping into squares that are very close to opponent.
        opp_next = d_cheb(nx, ny, ox, oy)

        # Resource adjacency bonus to encourage finishing turns.
        res_bonus = 0
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            if max(abs(nx - rx), abs(ny - ry)) == 1:
                res_bonus += 1

        # Deterministic tie-break by position order.
        sc = (our_d * 10 + race * 3 + opp_next * 2 - res_bonus, nx * 8 + ny)
        if best_sc is None or sc < best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]