def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "flee"))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles or not inside(x, y)

    def free_neighbors(x, y):
        c = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if not blocked(nx, ny):
                c += 1
        return c

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        fn = free_neighbors(nx, ny)
        # Directional bias to reduce "zigzag stalling"
        vx, vy = ox - sx, oy - sy
        dir_align = (1 if (nx - sx) * (vx if vx != 0 else 0) > 0 else 0) + (1 if (ny - sy) * (vy if vy != 0 else 0) > 0 else 0)
        # Corner preference: pursuer wants nearer corners when opponent is near corners; evader wants farther corners.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        dcorner = max(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
        dcorner_op = max(abs(ox - cx) + abs(oy - cy) for cx, cy in corners)

        if is_evader:
            # maximize survival: farther from opponent; prefer staying open; avoid giving opponent easy corner access
            primary = d
            secondary = fn
            tertiary = dcorner
            quaternary = -dcorner_op
        else:
            # minimize capture distance; prefer open squares; avoid moving to corner traps that reduce mobility
            primary = -d
            secondary = fn
            tertiary = -dcorner
            quaternary = dir_align

        key = (primary, secondary, tertiary, quaternary, -abs(nx - (w - 1)) - abs(ny - (h - 1)))
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]