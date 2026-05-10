def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Drift to a corner that is farther from opponent
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (manh(ox, oy, c[0], c[1]), -manh(sx, sy, c[0], c[1])))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if valid(sx + dx, sy + dy): 
            return [dx, dy]
        if valid(sx + dx, sy): 
            return [dx, 0]
        if valid(sx, sy + dy): 
            return [0, dy]
        return [0, 0]

    # Strategy: race when we can beat/deny; otherwise take safe resource where opponent is late.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Competitive (higher is better): positive if we are no worse by much
        competitive = do - ds
        # Prefer nearer targets when competitive, and "late-opponent" when not
        safe = do - ds if ds <= do + 1 else do  # if we can't contest, maximize opponent lateness
        key = (competitive * 10 + safe, -ds, -do, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Choose a move that reduces distance most while avoiding obstacles; tie-break by maximizing opponent distance.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = manh(nx, ny, tx, ty)
        no = manh(nx, ny, ox, oy)
        # Primary: minimize our distance to target; secondary: make opponent effectively "further" from us (avoid being boxed)
        key = (-ns, no, -manh(ox, oy, tx, ty), dx, dy)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]