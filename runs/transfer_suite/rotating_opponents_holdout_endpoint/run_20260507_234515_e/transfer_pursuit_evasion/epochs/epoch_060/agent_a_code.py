def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 1)) or 1
    h = int(observation.get("grid_height", 1)) or 1
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                oset.add((int(p[0]), int(p[1])))
            except:
                pass

    resources = observation.get("resources", []) or []
    rset = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                rset.append((int(p[0]), int(p[1])))
            except:
                pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_step(tx, ty, prefer_block=False):
        best = None
        best_score = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if not inside(nx, ny) or (nx, ny) in oset:
                    continue
                d = abs(nx - tx) + abs(ny - ty)
                score = d
                if prefer_block:
                    score = (d, abs(nx - ox) + abs(ny - oy))
                if best_score is None or score < best_score:
                    best_score = score
                    best = (dx, dy)
        return best

    target = None
    if rset:
        # deterministic nearest-resource target (tie-break by x,y)
        best = None
        bestd = None
        for rx, ry in rset:
            d = abs(sx - rx) + abs(sy - ry)
            if bestd is None or d < bestd or (d == bestd and (rx, ry) < best):
                bestd = d
                best = (rx, ry)
        target = best

    if target is not None:
        step = best_step(target[0], target[1])
        if step is not None:
            return [int(step[0]), int(step[1])]
    # fallback: move toward opponent if no resource step possible
    step = best_step(ox, oy, prefer_block=True)
    if step is not None:
        return [int(step[0]), int(step[1])]
    # last resort: stay or any valid move
    if inside(sx, sy) and (sx, sy) not in oset:
        return [0, 0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in oset:
                return [int(dx), int(dy)]
    return [0, 0]