def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = w - 1, h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny): return [dx, dy]
        for mx, my in cand:
            if valid(sx + mx, sy + my): return [mx, my]
        return [0, 0]

    best = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        best_for_move = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer strict advantage; then minimize our distance; then maximize gap.
            key = (sd >= od, - (od - sd), sd)
            if best_for_move is None or key < best_for_move[0]:
                best_for_move = (key, rx, ry, sd, od)
        if best_for_move is None:
            continue
        # Compare moves deterministically: primary by whether we can reach sooner; then by gap; then by our distance; then lexicographic move.
        key = (best_for_move[0][0], best_for_move[0][1], best_for_move[0][2], dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is not None:
        return best[1]

    # Fallback: head roughly toward the nearest resource while avoiding obstacles.
    nearest = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))
    rx, ry = nearest
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)
    nx, ny = sx + dx, sy + dy
    if valid(nx, ny): return [dx, dy]
    for mx, my in cand:
        if valid(sx + mx, sy + my): return [mx, my]
    return [0, 0]