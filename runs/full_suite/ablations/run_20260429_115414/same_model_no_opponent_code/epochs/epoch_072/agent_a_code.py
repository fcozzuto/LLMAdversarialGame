def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
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
    if not resources:
        # fallback: move toward board center
        resources = [(w // 2, h // 2)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose resource to maximize "self advantage": (opp_dist - self_dist), tie-break closer to self
    best = None
    best_adv = -10**9
    best_selfd = 10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and (sd < best_selfd or (sd == best_selfd and (rx, ry) < best))):
            best_adv = adv
            best_selfd = sd
            best = (rx, ry)
    tx, ty = best

    # Preferred delta: step that reduces Chebyshev distance to target, deterministic tie order
    dx0 = 0
    if tx > sx:
        dx0 = 1
    elif tx < sx:
        dx0 = -1
    dy0 = 0
    if ty > sy:
        dy0 = 1
    elif ty < sy:
        dy0 = -1

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # score: primarily minimize distance to target; secondarily maximize advantage over opponent at next position
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        adv2 = od2 - sd2
        # prefer landing exactly on target
        on = 0 if (nx, ny) == (tx, ty) else 1
        candidates.append((on, sd2, -adv2, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort()
    return [int(candidates[0][3]), int(candidates[0][4])]