def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role_self = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if is_evader:
        tx, ty = max(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), -c[0], -c[1]))
        best = None
        best_score = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dtar = cheb(nx, ny, tx, ty)
            dfro = cheb(nx, ny, ox, oy)
            score = dfro * 10 + dtar
            if best is None or score > best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # pursuer: minimize distance; tie-break by cutting off toward farthest corner of opponent
    target_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    tx, ty = target_corner[0], target_corner[1]
    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dcur = cheb(nx, ny, ox, oy)
        # Encourage moving so opponent has less escape: smaller distance to opponent's farthest corner
        dtx = cheb(nx, ny, tx, ty)
        score = (dcur, dtx, -nx, -ny, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)
    return list(best if best is not None else (0, 0))