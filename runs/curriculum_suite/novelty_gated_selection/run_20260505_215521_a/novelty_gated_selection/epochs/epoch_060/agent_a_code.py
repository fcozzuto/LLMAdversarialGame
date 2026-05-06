def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18
    opp_dist_now = cheb(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        if resources:
            best_gain = -10**18
            best_res_tie = (10**9, 10**9)
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                gain = od - sd  # positive => we are closer than opponent
                # tie-break: prefer higher gain, then closer resource, then deterministic coords
                if gain > best_gain or (gain == best_gain and (sd < best_res_tie[0] or (sd == best_res_tie[0] and (rx, ry) < best_res_tie[1]))):
                    best_gain = gain
                    best_res_tie = (sd, (rx, ry))
            # also slightly prefer increasing separation from opponent (prevents safe collector trapping)
            sep = cheb(nx, ny, ox, oy)
            score = (best_gain * 10_000) + (sep - opp_dist_now)
        else:
            score = (cheb(nx, ny, ox, oy) - opp_dist_now)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: prefer smaller movement then dx,dy ordering
            if (abs(dx), abs(dy), dx, dy) < (abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1]):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]