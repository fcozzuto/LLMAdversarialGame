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

    def cheb(x1, y1, x2, y2):
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

    tr = int(observation.get("turns_remaining", 0))
    best = None
    for rx, ry in valid:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer
        # Prefer immediate advantage; also lightly favor closer-to-we-do to finish.
        score = adv * 1000 - ds * 3 - (0 if tr <= 0 else max(0, ds - tr)) * 50
        if best is None or score > best[0] or (score == best[0] and (rx, ry) < best[1]):
            best = (score, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic preference order by evaluating moves then choosing best by fixed tuple ordering.
    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d1 = cheb(nx, ny, tx, ty)
        d2 = cheb(nx, ny, ox, oy)
        # Primary: reduce distance to target; Secondary: increase distance from opponent (avoid easy contest).
        key = (d1, -d2, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])
    if best_move is None:
        return [0, 0]
    return best_move[1]