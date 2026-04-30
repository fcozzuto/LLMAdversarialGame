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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = w // 2
        ty = h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        # Advantage score: prioritize resources where we are closer than opponent.
        adv = -10**9
        closest = 10**9
        opp_closest = 10**9
        for rx, ry in resources:
            dme = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            diff = dop - dme
            if diff > adv:
                adv = diff
            if dme < closest:
                closest = dme
            if dop < opp_closest:
                opp_closest = dop

        # If we can’t beat opponent on any nearby resource, fall back to staying closer overall
        score = 1000 * adv - 10 * closest + 2 * opp_closest

        # Tie-break: keep away from opponent when not clearly winning
        score -= 0.05 * cheb(nx, ny, ox, oy)

        if score > best_score:
            best_score = score
            best_move = [mx, my]

    if best_move == [0, 0]:
        # If all non-staying moves were blocked, try a deterministic valid direction toward center
        tx, ty = w // 2, h // 2
        mx = 0 if sx == tx else (1 if sx < tx else -1)
        my = 0 if sy == ty else (1 if sy < ty else -1)
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [mx, my]
    return [best_move[0], best_move[1]]