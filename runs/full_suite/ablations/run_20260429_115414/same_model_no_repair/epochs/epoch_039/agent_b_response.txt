def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2}
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_t = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in blocked:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive => we arrive earlier
        # Switch policy if we are generally behind: either take clear leads, else take closest safe.
        key = None
        if margin >= 1:
            # Strong deterministic preference: biggest lead; then smallest our distance; then smallest coords.
            key = (1, margin, -ds, -rx, -ry)
        else:
            # If no clear leads, prefer resources closer to us but less contested (opponent not too close).
            key = (0, -ds, -(abs(margin)), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        # Drift to a corner-adjacent center while avoiding obstacles.
        targets = [(3, 3), (4, 3), (3, 4), (4, 4)]
        for t in targets:
            if inb(t[0], t[1]) and t not in blocked:
                best_t = t
                break
        if best_t is None:
            return [0, 0]

    tx, ty = best_t
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, ox, oy)
        # Primary: minimize distance to target. Secondary: keep away from opponent to reduce contest.
        score = (0 - ns, no, -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]