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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    best_targets = []
    for rx, ry in valid:
        ds = cheb_dist(sx, sy, rx, ry)
        do = cheb_dist(ox, oy, rx, ry)
        # Prefer resources we can reach earlier than opponent; otherwise take closest to us.
        if ds <= do and (tr <= 0 or ds <= tr):
            best_targets.append((do - ds, -ds, rx, ry))
        else:
            best_targets.append((-(ds), -do, rx, ry))
    best_targets.sort(reverse=True)
    tx, ty = best_targets[0][2], best_targets[0][3]

    candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    candidates.sort(key=lambda d: (0 if d == (0, 0) else 1, d[0], d[1]))

    best_move = (0, 0)
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_to_target = cheb_dist(nx, ny, tx, ty)
        d_opp = cheb_dist(nx, ny, ox, oy)
        # Higher advantage: reduce distance to target, keep separation from opponent.
        score = (-(d_to_target), -(d_opp), nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]