def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        tx, ty = w - 1 - ox + sx, h - 1 - oy + sy
        tx = tx if 0 <= tx < w else w - 1
        ty = ty if 0 <= ty < h else h - 1
        best_t = (tx, ty)
    else:
        best_score = None
        best_t = resources[0]
        for rx, ry in resources:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources closer to us and "less" close to opponent; deterministic tie-break by coord
            score = (md - 0.65 * od, md, rx, ry)
            if best_score is None or score < best_score:
                best_score = score
                best_t = (rx, ry)

    tx, ty = best_t
    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    candidates = []
    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            continue
        # Score move by resulting distance to chosen target, with slight penalty for moving away
        nd = cheb(nx, ny, tx, ty)
        away_pen = 0
        if (ddx != 0 and ((sx + ddx) - tx) * (sx - tx) > 0) or (ddy != 0 and ((sy + ddy) - ty) * (sy - ty) > 0):
            away_pen = 1
        candidates.append((nd + away_pen, ddx, ddy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    _, bdX, bdY = candidates[0]
    return [int(bdX), int(bdY)]