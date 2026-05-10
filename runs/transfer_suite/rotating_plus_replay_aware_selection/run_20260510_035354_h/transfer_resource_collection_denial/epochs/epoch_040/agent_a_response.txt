def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_target = None
    best_tkey = None

    # Choose a resource we can reach before (or not too far after) opponent.
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer closer to us, but avoid resources opponent can beat decisively.
        beat_margin = do - ds  # positive means we are closer
        # Also slightly prefer being nearer to resource overall.
        k = (-(beat_margin > 0), -beat_margin, ds, rx, ry)
        if best_tkey is None or k < best_tkey:
            best_tkey = k
            best_target = (rx, ry)

    rx, ry = best_target
    # Move one step to reduce distance to chosen target, with safety/denial pressure.
    best_move = (0, 0)
    best_mkey = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_next = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        beat_margin_next = do - ds_next
        # If opponent can reach immediately, prefer moves that keep ds small but don't blunder into obstacles.
        # Tie-break: minimize distance and then lexicographically.
        # Convert to a comparable key: smaller is better.
        k = (-(beat_margin_next > 0), -beat_margin_next, ds_next, nx, ny)
        if best_mkey is None or k < best_mkey:
            best_mkey = k
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]