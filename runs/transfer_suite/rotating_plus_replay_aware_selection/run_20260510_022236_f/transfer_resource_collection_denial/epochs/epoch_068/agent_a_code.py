def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    tr = int(observation.get("turns_remaining", 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in valid:
        ds = cheb_dist(sx, sy, rx, ry)
        do = cheb_dist(ox, oy, rx, ry)
        # Prefer resources where we are closer; if contested, we want the biggest advantage.
        # Also slightly prefer those we can reach earlier in remaining time.
        time_bonus = 0
        if tr > 0:
            if ds <= tr:
                time_bonus = 1
            else:
                time_bonus = -1
        key = (do - ds, -ds, time_bonus, do, -((rx + ry) & 1))
        if best is None or key > best_key:
            best, best_key = (rx, ry), key

    tx, ty = best
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Choose a move that best reduces distance to target while avoiding obstacles.
    cur_d = cheb_dist(sx, sy, tx, ty)
    bestm = (0, 0)
    bestm_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = cheb_dist(nx, ny, tx, ty)
        # Secondary: if opponent could grab the target sooner, consider reducing that too.
        ndo = cheb_dist(ox, oy, tx, ty)
        key = (cur_d - nd, -nd, -(ndo - nd), -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)))
        if bestm_key is None or key > bestm_key:
            bestm_key = key
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]