def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    role = (observation.get("self_role") or "").lower()
    evader = ("evad" in role) or ("escape" in role) or ("runner" in role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        res_bonus = 0
        if resources and not evader:
            mind = 10**9
            for rx, ry in resources:
                dd = cheb(nx, ny, rx, ry)
                if dd < mind:
                    mind = dd
            res_bonus = -0.05 * mind
        elif resources and evader:
            mind = 10**9
            for rx, ry in resources:
                dd = cheb(nx, ny, rx, ry)
                if dd < mind:
                    mind = dd
            res_bonus = -0.01 * mind  # slight preference to not run too far from potential blocks

        # add a tiny deterministic preference to break ties: favor diagonal progress toward/away
        diag_pref = 0.001 * (abs(dx) + abs(dy))
        stay_pen = 0.001 if (dx == 0 and dy == 0) else 0.0

        if evader:
            score = (-d) + res_bonus + diag_pref - stay_pen
        else:
            score = d + res_bonus - stay_pen

        # deterministically pick: smallest score for pursuer, largest distance for evader via score formulation
        if best is None or score < best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]