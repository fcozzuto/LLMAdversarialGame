def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    best = None
    best_key = None
    # Prefer resources we are closer to; break ties by opponent being farther.
    # Add slight preference to closer to being reached (smaller dist).
    for rx, ry in valid:
        ds = cheb_dist(sx, sy, rx, ry)
        do = cheb_dist(ox, oy, rx, ry)
        # If opponent is already at same distance, we may lose; penalize that.
        key = (do - ds, -ds, do)  # maximize (do-ds), minimize ds and do
        if best is None or key > best_key:
            best, best_key = (rx, ry), key

    rx, ry = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_pair = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nds = cheb_dist(nx, ny, rx, ry)
        ndo = cheb_dist(ox, oy, rx, ry)
        # Secondary: if equal approach, move to reduce distance to opponent's position slightly (safety).
        safety = cheb_dist(nx, ny, ox, oy)
        pair = (nds, ndo, safety, dx == 0 and dy == 0)
        if best_pair is None or pair < best_pair:
            best_pair = pair
            best_move = [dx, dy]

    return best_move