def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Choose a target resource: prioritize where we're ahead (opp_d - our_d), then closer.
    best = None
    best_key = None
    for x, y in resources:
        our_d = man(sx, sy, x, y)
        opp_d = man(ox, oy, x, y)
        adv = opp_d - our_d
        key = (-(adv * 1000 + (opp_d > our_d) * 100), our_d, x, y)  # deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)
    tx, ty = best

    # Pick the move that best improves our capture prospects and progress to target.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestmk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        our_d2 = man(nx, ny, tx, ty)
        opp_d2 = man(ox, oy, tx, ty)
        prog = man(sx, sy, tx, ty) - our_d2  # positive is good
        # also lightly discourage moving into a resource that opponent is much closer to
        block_pen = 0
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                da = man(nx, ny, rx, ry)
                db = man(ox, oy, rx, ry)
                if db < da:
                    block_pen = 10
                break
        key = (-(prog * 1000 + (opp_d2 - our_d2) * 10), our_d2, block_pen, dx, dy)
        if bestmk is None or key < bestmk:
            bestmk = key
            bestm = (dx, dy)

    dx, dy = bestm
    if not isinstance(dx, int) or not isinstance(dy, int) or dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [dx, dy]