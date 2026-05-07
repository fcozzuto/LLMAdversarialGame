def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    if (sx, sy) in resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    candidates_win = []
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = do - ds
        candidates_win.append((adv, -ds, rx, ry))
    candidates_win.sort(reverse=True)
    target = None
    for adv, nds, rx, ry in candidates_win:
        if adv > 0:
            target = (rx, ry)
            break
    if target is None:
        # Deny: head to the resource the opponent can reach fastest
        best = None
        for adv, nds, rx, ry in candidates_win:
            do = dist(ox, oy, rx, ry)
            key = (-do, do, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        target = best[1]

    tx, ty = target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    best_move = (10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        step = abs(dx) + abs(dy)
        # Prefer reducing distance; then prefer fewer movement components; then lex order
        key = (d, step, dx, dy)
        if key < best_move:
            best_move = key

    return [int(best_move[2]), int(best_move[3])]