def choose_move(observation):
    def ti(v, d=0):
        try:
            return int(v)
        except:
            return d

    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = ti(sx), ti(sy), ti(ox), ti(oy)
    w = ti(observation.get("grid_width", 0), 8) or 8
    h = ti(observation.get("grid_height", 0), 8) or 8

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
            if inb(x, y):
                obs_set.add((x, y))

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = ti(r[0]), ti(r[1])
            if inb(x, y) and (x, y) not in obs_set:
                targets.append((x, y))
    if not targets:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_cell = None
    best_adv = None
    for tx, ty in targets:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd  # prefer resources where we are closer than opponent
        # tie-break: prefer smaller distance for us, then farther from opponent
        key = (adv, -sd, -(cheb(ox, oy, tx, ty)))
        if best_cell is None or key > best_adv:
            best_cell = (tx, ty)
            best_adv = key

    tx, ty = best_cell
    # choose move that improves ability to reach target first; avoid obstacles
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        adv2 = od2 - sd2
        # slight bias to move closer to target on both axes (more "direct" path)
        direct = - (abs(nx - tx) + abs(ny - ty))
        score = (adv2, -sd2, direct)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_score is not None else [0, 0]