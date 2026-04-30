def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    # Pick target that maximizes (opponent advantage - our disadvantage), tie-break deterministically.
    best = None
    for tx, ty in resources:
        our_d = cheb(sx, sy, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        adv = opp_d - our_d
        score = (adv, -our_d, -(abs(tx - sx) + abs(ty - sy)), tx, ty)
        if best is None or score > best[0]:
            best = (score, tx, ty, our_d)

    if best is None:
        return [0, 0]

    _, tx, ty, _ = best

    # Greedy step toward target with deterministic tie-breaking.
    sdx = 0 if tx == sx else (1 if tx > sx else -1)
    sdy = 0 if ty == sy else (1 if ty > sy else -1)
    preferred = []
    for ddx, ddy in dirs:
        if ddx == 0 and ddy == 0:
            preferred.append((0, ddx, ddy))
            continue
        # Prefer moves that align with direction to target
        align = 0
        if ddx == sdx: align += 2
        if ddy == sdy: align += 2
        # Slight preference for diagonal if both aligned
        if ddx == sdx and ddy == sdy: align += 1
        preferred.append((align, ddx, ddy))

    candidates = []
    for align, dx, dy in sorted(preferred, reverse=True):
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        # Primary minimize distance; secondary maximize alignment; then deterministic by dx,dy
        candidates.append((d_to_target, -align, dx, dy))
    if not candidates:
        # Stay if completely blocked
        return [0, 0]

    candidates.sort()
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]