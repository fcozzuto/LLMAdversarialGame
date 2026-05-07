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
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    if not resources:
        return [0, 0]

    best = None
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs_set:
            continue
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - md  # higher => we arrive sooner
        # tie-break deterministically by target coords
        cand = (adv, -md, tx, ty)
        if best is None or cand > best[0]:
            best = (cand, tx, ty)

    if best is None:
        return [0, 0]
    _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best_step = (0, 0)
    best_dist = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_dist:
            best_dist = d
            best_step = (dx, dy)
    return [int(best_step[0]), int(best_step[1])]