def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_toward(posx, posy):
        if not resources:
            tx, ty = (w - 1, h - 1) if posx < w // 2 else (0, 0)
            dx = 0 if tx == posx else (1 if tx > posx else -1)
            dy = 0 if ty == posy else (1 if ty > posy else -1)
            return dx, dy
        bx, by = resources[0]
        bestd = man(posx, posy, bx, by)
        for rx, ry in resources[1:]:
            d = man(posx, posy, rx, ry)
            if d < bestd:
                bestd, bx, by = d, rx, ry
        dx = 0 if bx == posx else (1 if bx > posx else -1)
        dy = 0 if by == posy else (1 if by > posy else -1)
        return dx, dy

    opp_dx, opp_dy = best_toward(ox, oy)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    opp_nx, opp_ny = ox + opp_dx, oy + opp_dy
    if not valid(opp_nx, opp_ny):
        opp_nx, opp_ny = ox, oy
        opp_dx, opp_dy = 0, 0

    # One-step evaluation: advantage in getting the nearest resource, with contest pressure.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if (nx, ny) in obstacles:
            continue

        my_on = 1 if (nx, ny) in resources else 0

        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            my_best = min(my_best, man(nx, ny, rx, ry))
            opp_best = min(opp_best, man(opp_nx, opp_ny, rx, ry))

        # If we land on a resource, strongly prefer; otherwise move to reduce our nearest and make it harder for opponent.
        val = 0
        val += my_on * 1000
        val += (opp_best - my_best) * 10

        # Extra contest: if we are closer to the opponent's target than they would be, prefer.
        if resources:
            tx, ty = min(resources, key=lambda p: man(ox, oy, p[0], p[1]))
            if man(nx, ny, tx, ty) <= man(opp_nx, opp_ny, tx, ty):
                val += 8

        # Deter moving into immediate proximity to opponent while we aren't collecting.
        if my_on == 0:
            val -= max(0, 3 - man(nx, ny, ox, oy)) * 3

        # Deterministic tie-break: prefer staying or moves with smallest (dx,dy) in lexicographic order.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]