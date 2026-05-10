def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    def adj_obst(x, y):
        for dx in (-1, 0, 1):
            nx = x + dx
            for dy in (-1, 0, 1):
                ny = y + dy
                if dx == 0 and dy == 0:
                    continue
                if (nx, ny) in obs:
                    return 1
        return 0

    if not resources:
        return [0, 0]

    best = None
    best_score = None
    for p in resources:
        if not (isinstance(p, (list, tuple)) and len(p) >= 2):
            continue
        tx, ty = int(p[0]), int(p[1])
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        d_self = cheb(sx, sy, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        if d_self == 0:
            return [0, 0]
        # Prefer resources we can reach sooner than opponent; penalize being near obstacles
        score = (d_opp - d_self) * 100 - d_self - 7 * adj_obst(tx, ty)
        if best is None or score > best_score:
            best = (tx, ty)
            best_score = score

    tx, ty = best if best is not None else (sx, sy)
    if (sx, sy) == (tx, ty):
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        # Reduce our distance; if tied, move that makes opponent effectively farther (via us choosing harder-to-contest paths)
        val = (-nd, -(oppd + (nd == 0)), -adj_obst(nx, ny), -dx*dx - dy*dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]