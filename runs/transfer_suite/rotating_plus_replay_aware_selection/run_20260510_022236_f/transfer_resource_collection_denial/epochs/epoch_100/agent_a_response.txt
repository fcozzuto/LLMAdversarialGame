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

    valid_resources = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid_resources.append((x, y))
    if not valid_resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy

        # Choose the resource that gives us the best immediate lead after this move.
        best_res_key = None
        for rx, ry in valid_resources:
            ds = cheb_dist(nx, ny, rx, ry)
            do = cheb_dist(ox, oy, rx, ry)
            # Prefer taking/contesting resources where we are not slower; otherwise deny by maximizing opponent distance.
            lead = do - ds  # higher is better
            # Secondary: smaller our distance (faster collection), then smaller opponent distance (deny).
            key = (lead, -ds, -do)
            if best_res_key is None or key > best_res_key:
                best_res_key = key

        # Tie-break between moves: primarily the resource lead, then our distance to that best resource.
        key = best_res_key
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move