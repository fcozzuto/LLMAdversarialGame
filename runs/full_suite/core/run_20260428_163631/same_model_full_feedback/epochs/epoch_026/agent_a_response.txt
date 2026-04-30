def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = (w - 1 if sx < w - 1 else 0), (h - 1 if sy < h - 1 else 0)
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            v = man(nx, ny, tx, ty)
            if bestv is None or v < bestv:
                bestv, best = v, (dx, dy)
        return list(best)

    # Target selection: prioritize resources where we are relatively closer than opponent.
    best_t = None
    best_score = None
    for rx, ry in resources:
        d_me = man(sx, sy, rx, ry)
        d_op = man(ox, oy, rx, ry)
        # If we can potentially beat opponent, strongly favor; otherwise pick the closest we can reach.
        score = (d_op - d_me) * 100 - d_me * 2
        if best_score is None or score > best_score:
            best_score, best_t = score, (rx, ry)

    tr, tc = best_t
    # Move selection: choose step that reduces distance to target; add avoidance of opponent proximity and obstacle tangles.
    best = None
    bestv = None
    for dx, dy, nx, ny in legal:
        d_to = man(nx, ny, tr, tc)
        d_op = man(nx, ny, ox, oy)
        # Slightly punish moves that allow opponent to be closer to the same target.
        opp_after = man(ox, oy, tr, tc)
        me_after = d_to
        v = d_to * 3 - d_op * 0.7
        v += (me_after - opp_after) * 1.5
        # If opponent is very close, prefer moves that increase separation.
        if d_op <= 2:
            v -= 20
        if bestv is None or v < bestv:
            bestv, best = v, (dx, dy)
    return [int(best[0]), int(best[1])]