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

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        # fallback: drift toward center while staying obstacle-safe
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if -d > best[2]:
                best = (dx, dy, -d)
        return [best[0], best[1]]

    # choose target greedily by advantage over opponent
    best_target = None
    best_adv = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = (od - sd) * 1000 - sd  # strongly prefer nearer than opponent
        if adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)

    rx, ry = best_target
    best_move = (0, 0, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # also consider alternative resources closer to us after move
        alt_bonus = 0
        for ax, ay in resources:
            if (ax, ay) == (rx, ry):
                continue
            if cheb(nx, ny, ax, ay) <= sd:
                alt_bonus += 1
        val = (od - sd) * 1000 - sd + alt_bonus * 2 - cheb(nx, ny, ox, oy) * 0.05
        if val > best_move[2]:
            best_move = (dx, dy, val)

    return [int(best_move[0]), int(best_move[1])]