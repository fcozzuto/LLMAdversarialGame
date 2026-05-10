def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    srole = (observation.get("self_role") or "").lower()
    evader = ("evader" in srole) or ("runner" in srole) or ("evasive" in srole) or ("evasion" in srole)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
            if 0 <= tx < w and 0 <= ty < h:
                targets.append((tx, ty))
        elif isinstance(r, dict):
            p = r.get("position") or r.get("pos")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                tx, ty = int(p[0]), int(p[1])
                if 0 <= tx < w and 0 <= ty < h:
                    targets.append((tx, ty))

    best = None
    bestv = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        oppd = man(nx, ny, ox, oy)
        if targets:
            mind = min(man(nx, ny, tx, ty) for tx, ty in targets)
            score = -mind
        else:
            score = 0
        if evader:
            score += 2 * oppd
        else:
            score += -2 * oppd
        if score > bestv or (score == bestv and (dx, dy) == (0, 0)):
            bestv = score
            best = [dx, dy]
    return best if best is not None else [0, 0]