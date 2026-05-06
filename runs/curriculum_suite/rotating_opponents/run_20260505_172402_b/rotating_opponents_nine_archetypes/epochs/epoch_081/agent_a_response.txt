def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_for(posx, posy):
        best = None
        bscore = None
        for rx, ry in resources:
            sd = cheb(posx, posy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach no slower; break ties toward being closer.
            # Encourage stealing: larger (od - sd) is better.
            steal = od - sd
            # Slightly penalize staying far overall to avoid dithering.
            score = (steal * 1000) - sd
            if (bscore is None) or (score > bscore) or (score == bscore and (sd < best[0])):
                bscore = score
                best = (sd, rx, ry)
        return best[1], best[2]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: iterate in a fixed order.
    best_move = [0, 0]
    best_val = None
    cur_target = best_for(sx, sy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        tx, ty = cur_target
        # One-step lookahead: choose the move that improves the best "steal" target from the next position.
        nx_target = best_for(nx, ny)
        tx2, ty2 = nx_target

        sd1 = cheb(nx, ny, tx2, ty2)
        od1 = cheb(ox, oy, tx2, ty2)
        steal1 = od1 - sd1
        # Secondary objective: if targets differ, prefer moving toward a target that we can reach earlier.
        same_target_bonus = 1 if (tx2 == tx and ty2 == ty) else 0

        # Additional obstacle-ish safety: prefer not increasing distance to nearest obstacle-adjacent cell.
        # (Lightweight: just compute min cheb to any obstacle.)
        mind = None
        if obstacles:
            for ox2, oy2 in obstacles:
                d = cheb(nx, ny, ox2, oy2)
                if mind is None or d < mind:
                    mind = d
        safety = 0 if mind is None else (mind if mind < 3 else 3)

        val = (steal1 * 10000) + (same_target_bonus * 100) + (safety * 10) - sd1
        if (best_val is None) or (val > best_val):
            best_val = val
            best_move = [dx, dy]

    return best_move