def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obstacle_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid_pos(x, y):
        return inb(x, y) and (x, y) not in obstacle_set

    if not resources:
        return [0, 0]

    rem = observation.get("remaining_resource_count", len(resources))
    best_key = None
    tx = ty = resources[0][0], resources[0][1]

    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive => we reach earlier
        # Scarce resources: strongly prefer securing before opponent.
        if rem <= 4:
            key = (0 if margin > 0 else 1, -margin, ds, rx, ry)
        else:
            key = (1 if margin <= 0 else 0, -margin, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            tx, ty = rx, ry

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid_pos(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Prefer moves that reduce our distance; if tied, improve "reach before opponent".
        margin = no - ns
        # Also lightly prefer moving generally toward the target quadrant.
        quad = abs((tx - nx) > 0) + abs((ty - ny) > 0)
        key = (ns, -margin, quad, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]