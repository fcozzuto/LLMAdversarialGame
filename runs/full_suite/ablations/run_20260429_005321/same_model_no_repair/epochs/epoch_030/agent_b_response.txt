def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    # Pick a deterministic target resource that we can reach earlier than the opponent.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer large positive (opponent farther than us), then closer.
        score = (do - ds) * 1000 - ds
        # Tie-break deterministically with coordinates.
        score -= (rx * 31 + ry)
        if best is None or score > best[0]:
            best = (score, rx, ry)
    _, tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Evaluate each move: progress to target, keep away from opponent, avoid obstacles.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            val = -10**18
        else:
            d_t = man(nx, ny, tx, ty)
            d_o = man(nx, ny, ox, oy)
            # Encourage reduction in distance to target; discourage proximity to opponent.
            # Also slight preference for moving toward center to break ties.
            cx, cy = (gw - 1) / 2.0, (gh - 1) / 2.0
            center_pen = abs(nx - cx) + abs(ny - cy)
            val = -d_t * 10 + d_o - center_pen * 0.01
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]