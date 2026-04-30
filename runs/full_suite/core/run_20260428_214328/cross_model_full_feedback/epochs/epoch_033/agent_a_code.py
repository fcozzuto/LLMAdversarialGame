def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = {(int(p[0]), int(p[1])) for p in obstacles if p is not None and len(p) >= 2}

    resources = observation.get("resources", []) or []
    res = [(int(p[0]), int(p[1])) for p in resources if p is not None and len(p) >= 2]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst and (nx, ny) != (ox, oy):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best = None
    best_key = None

    for dx, dy, nx, ny in legal:
        if res:
            dself = min(cheb(nx, ny, rx, ry) for rx, ry in res)
            dopp = cheb(ox, oy, nx, ny)
            dopp_to_res = min(cheb(ox, oy, rx, ry) for rx, ry in res)
            # Prioritize immediate capture / progress; also prevent opponent from being closer
            key = (0,)
            immediate = 1 if any((nx, ny) == (rx, ry) for rx, ry in res) else 0
            # Score to maximize: immediate capture, reduce distance to resource, increase opponent separation
            score = immediate * 100000 + (-dself) * 1000 + (dopp_to_res - dself) * 100 + (dopp) * 2
            tie = cheb(nx, ny, ox, oy)
            key = (score, -tie, dx, dy)
        else:
            # No resources: avoid staying put if possible, move away from opponent
            dopp = cheb(nx, ny, ox, oy)
            score = doppel = dopp * 1000 - (abs(dx) + abs(dy)) * 3
            key = (score, -cheb(nx, ny, sx, sy), dx, dy)

        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]