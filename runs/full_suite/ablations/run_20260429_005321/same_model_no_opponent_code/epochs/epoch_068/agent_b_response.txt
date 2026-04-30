def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best_dx, best_dy = 0, 0
    best_score = -10**18

    if resources:
        for dx, dy, nx, ny in moves:
            score = -d2(nx, ny, ox, oy) * 0.02  # slight prefer staying farther from opponent
            for tx, ty in resources:
                ds = d2(nx, ny, tx, ty)
                do = d2(ox, oy, tx, ty)
                advantage = do - ds  # positive means we are closer to that resource
                pick = (1 if ds == 0 else 0)
                score = max(score, pick * 1_000_000 + advantage * 6 - ds * 0.25)
            if score > best_score:
                best_score = score
                best_dx, best_dy = dx, dy
    else:
        # No visible resources: move deterministically toward opponent side (opposite corner bias)
        target = (0 if sx > w // 2 else w - 1, 0 if sy > h // 2 else h - 1)
        tx, ty = target
        for dx, dy, nx, ny in moves:
            score = -d2(nx, ny, tx, ty)
            if score > best_score:
                best_score = score
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]