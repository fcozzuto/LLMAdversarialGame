def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target = None
    if resources:
        best_adv = None
        for x, y in resources:
            our_d = cheb(sx, sy, x, y)
            opp_d = cheb(ox, oy, x, y)
            adv = opp_d - our_d  # positive => we're closer than opponent
            if best_adv is None or adv > best_adv:
                best_adv = adv
                target = (x, y)

    if target is None:
        # No visible resources: drift to center to avoid being trapped.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_move = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, cx, cy)
            if best is None or d < best:
                best = d
                best_move = [dx, dy]
        return best_move

    tx, ty = target
    opp_to_target = cheb(ox, oy, tx, ty)

    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        our_d = cheb(nx, ny, tx, ty)
        # Immediate pickup if we're on a resource square.
        immediate = 1 if any(rx == nx and ry == ny for rx, ry in resources) else 0
        # Prefer moves that reduce opponent contestability by also staying farther from opponent.
        our_to_opp = cheb(nx, ny, ox, oy)
        # Move score: prioritize immediate, then being closer to target, and keeping distance from opponent.
        score = immediate * 1000 + (opp_to_target - our_d) * 20 + our_to_opp * 0.5 - our_d * 1.5
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move