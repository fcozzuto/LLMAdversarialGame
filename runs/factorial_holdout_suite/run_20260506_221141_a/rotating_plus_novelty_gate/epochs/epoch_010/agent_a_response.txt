def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
        except Exception:
            continue
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        adx = dx if dx >= 0 else -dx
        ady = dy if dy >= 0 else -dy
        return adx if adx > ady else ady

    if not resources:
        return [0, 0]

    best_tx, best_ty = None, None
    best_score = None
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs_set:
            continue
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer resources we can reach sooner; tie-break deterministically.
        score = (od - md, -md, -cheb(ox, oy, sx, sy), tx, ty)
        if best_score is None or score > best_score:
            best_score = score
            best_tx, best_ty = tx, ty

    if best_tx is None:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_step = [0, 0]
    best_step_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue
        md2 = cheb(nx, ny, best_tx, best_ty)
        od2 = cheb(ox, oy, best_tx, best_ty)
        # Also avoid stepping into obvious dead zones near obstacles.
        danger = 0
        for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            px, py = nx + ax, ny + ay
            if 0 <= px < w and 0 <= py < h and (px, py) in obs_set:
                danger += 1
        step_score = (od2 - md2, -md2, -danger, -cheb(nx, ny, ox, oy), dx, dy)
        if best_step_score is None or step_score > best_step_score:
            best_step_score = step_score
            best_step = [dx, dy]

    return best_step