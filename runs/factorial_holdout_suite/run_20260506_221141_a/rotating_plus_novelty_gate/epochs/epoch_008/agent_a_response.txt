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
        a, b = (dx if dx >= 0 else -dx), (dy if dy >= 0 else -dy)
        return a if a > b else b

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    if not resources:
        return [0, 0]

    best_cand = None
    best_tx, best_ty = sx, sy
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not inb(tx, ty):
            continue
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - md  # positive => we arrive sooner
        cand = (adv, -md, tx, ty)
        if best_cand is None or cand > best_cand:
            best_cand = cand
            best_tx, best_ty = tx, ty

    tx, ty = best_tx, best_ty
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    cur_d = cheb(sx, sy, tx, ty)
    best_step = (0, 0)
    best_key = (-10**9, 10**9, 0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        closer = cur_d - nd
        # Prefer maximal closer; then minimal remaining distance; then deterministic coords
        key = (closer, -nd, dx, dy)
        if key > best_key:
            best_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]