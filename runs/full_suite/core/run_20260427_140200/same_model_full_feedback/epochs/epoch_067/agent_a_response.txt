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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick best target by current advantage (opponent distance minus ours).
    best_target = None
    best_adv = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if best_adv is None or adv > best_adv or (adv == best_adv and (rx, ry) < best_target):
            best_adv = adv
            best_target = (rx, ry)

    if best_target is None:
        # No resources: move toward center while avoiding opponent.
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        best_move = [0, 0]
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = -cheb(nx, ny, tx, ty) + 0.5 * cheb(nx, ny, ox, oy)
            if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
                best_score = score
                best_move = [dx, dy]
        return best_move

    rx, ry = best_target

    # Evaluate each move by post-move advantage for the chosen target, then by separation from opponent.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_d = cheb(nx, ny, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        adv = opp_d - self_d
        sep = cheb(nx, ny, ox, oy)
        # If we're tied on advantage, prefer higher separation and then closer to the target.
        score = adv * 1000 + sep - self_d
        if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]
    return best_move