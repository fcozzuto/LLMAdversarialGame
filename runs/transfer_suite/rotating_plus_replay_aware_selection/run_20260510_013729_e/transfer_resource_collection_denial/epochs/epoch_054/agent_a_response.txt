def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res_sorted = sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1]))
    opp_to = {}
    for rx, ry in res_sorted:
        opp_to[(rx, ry)] = cheb(ox, oy, rx, ry)

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_val = -10**18
    best_move = [0, 0]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            val = -10**12
        else:
            self_best = 0.0
            for rx, ry in res_sorted:
                ds = cheb(nx, ny, rx, ry)
                do = opp_to[(rx, ry)]
                lead = do - ds  # positive: we reach sooner
                cap = 4.0 if (nx, ny) == (rx, ry) else 0.0
                # small extra preference for reducing distance to opponent's nearest resource
                proximity_push = 0.08 * cheb(nx, ny, ox, oy)
                # discourage moving into "far from all resources"
                val_r = cap + 2.7 * lead - 0.35 * ds - proximity_push
                if val_r > self_best:
                    self_best = val_r
            val = self_best
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            # deterministic tie-break: prefer staying or smaller lexicographic move
            if best_move == [0, 0] and [dx, dy] != [0, 0]:
                pass
            else:
                if (dx, dy) < (best_move[0], best_move[1]):
                    best_move = [dx, dy]

    return best_move