def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_move = (0, 0)

    # If no visible resources, just move toward opponent's side but keep distance.
    drift_target = (w - 1, h - 1) if sx + sy <= ox + oy else (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        if resources:
            # Choose the resource that maximizes "advantage": opponent_dist - my_dist.
            best_adv = None
            best_my_d = None
            for rx, ry in resources:
                my_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                adv = opp_d - my_d
                if (best_adv is None or adv > best_adv or
                    (adv == best_adv and (best_my_d is None or my_d < best_my_d))):
                    best_adv = adv
                    best_my_d = my_d
            # Move score: primary advantage, then distance tie-break, then keep away from opponent.
            my_opp_d = cheb(nx, ny, ox, oy)
            score = (best_adv * 1000) - (best_my_d * 10) + my_opp_d
        else:
            my_opp_d = cheb(nx, ny, ox, oy)
            to_t = cheb(nx, ny, drift_target[0], drift_target[1])
            score = (my_opp_d * 10) - to_t

        if best is None or score > best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]