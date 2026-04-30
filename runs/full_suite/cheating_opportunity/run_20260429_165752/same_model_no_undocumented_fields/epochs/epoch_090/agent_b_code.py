def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ti = int(observation.get("turn_index") or 0)
    if ti % 2:
        moves = moves[3:] + moves[:3]

    target = None
    best_adv = -10**18
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        adv = do - ds  # prefer resources opponent reaches later
        if adv > best_adv:
            best_adv = adv
            target = (x, y)
        elif adv == best_adv and target is not None:
            if ds < cheb(sx, sy, target[0], target[1]):
                target = (x, y)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if target is None:
            # fallback: drift toward center while keeping distance from opponent
            sc = -cheb(nx, ny, cx, cy) + 0.1 * cheb(nx, ny, ox, oy)
        else:
            tx, ty = target
            if (nx, ny) == (tx, ty):
                return [dx, dy]
            new_ds = cheb(nx, ny, tx, ty)
            cur_ds = cheb(sx, sy, tx, ty)
            # prefer reducing self distance to target; also discourage helping opponent by allowing closer approach
            sc = 1000 * (cur_ds - new_ds) + 5 * best_adv - 0.2 * cheb(nx, ny, ox, oy)

        # deterministic tie-break
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)
        elif sc == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]