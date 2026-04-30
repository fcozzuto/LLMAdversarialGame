def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def d(a, b, c, d_):
        dx = a - c
        dy = b - d_
        return (dx * dx + dy * dy)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_target = None
    best_score = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = d(sx, sy, rx, ry)
        do = d(ox, oy, rx, ry)
        # Prefer resources we're closer to AND opponent is relatively far.
        sc = (do - ds, -do, -ds, rx, ry)
        if best_score is None or sc > best_score:
            best_score = sc
            best_target = (rx, ry)
    if best_target is None:
        # No resources; chase opponent if possible else hold
        tx, ty = ox, oy
    else:
        tx, ty = best_target
    # Choose move that gets closer to target while not moving into obstacles, with slight anti-opponent bias
    best_move = (0, 0)
    best_msc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_to = d(nx, ny, tx, ty)
        dist_opp = d(nx, ny, ox, oy)
        # Anti-opponent: prefer keeping distance from opponent and improving target progress
        msc = (-dist_to, dist_opp, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_msc is None or msc > best_msc:
            best_msc = msc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]