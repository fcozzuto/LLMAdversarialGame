def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obstacle_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacle_set

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    rem = observation.get("remaining_resource_count", len(resources))
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive => we arrive earlier
        # Early-game: more opportunistic on positive margin; Late-game: stronger race for nearest.
        if rem <= 4:
            key = (0 if margin >= 0 else 1, -margin, ds, rx, ry)
        else:
            key = (0 if margin >= 0 else 1, -margin if margin >= 0 else (ds - do), ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), ds, do)
    tx, ty = best[1]

    # Candidate next moves: prefer move that most reduces distance to target.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and not blocked(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    best_move = None
    best_dist = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, tx, ty)
        # Secondary: if we can keep within our lead vs opponent, prefer that.
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        lead_score = no - ns
        key = (d, -lead_score, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_dist is None or key < best_dist:
            best_dist = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]