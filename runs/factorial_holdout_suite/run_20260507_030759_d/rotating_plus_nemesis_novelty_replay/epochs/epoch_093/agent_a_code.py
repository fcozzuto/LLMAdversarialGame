def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            oxp, oyp = int(o[0]), int(o[1])
            if 0 <= oxp < w and 0 <= oyp < h:
                obstacles.add((oxp, oyp))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If we can "own" a resource (arrive no later than opponent), prefer it.
    # Else, pick a resource with best relative gain and strategic bias to avoid mirroring sweep behavior.
    parity_bias = ((sx + sy) & 1) * 0.01
    best = None
    best_val = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive means we arrive earlier
        # Bias toward resources that differ in row/col from opponent to reduce collision.
        rowdiff = abs(ry - oy)
        coldiff = abs(rx - ox)
        # Deterministic tie-break: also prefer "more remote" diagonals from opponent.
        diag_away = (abs((rx - ox) + (ry - oy)) + abs((rx - ox) - (ry - oy))) * 0.001
        val = lead * 10.0 + (rowdiff - coldiff) * 0.05 + diag_away + parity_bias
        if best is None or val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    # Choose a move that is valid and reduces distance; tie-break by deterministic order.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curd = cheb(sx, sy, tx, ty)
    best_step = (0, 0)
    best_step_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Primary: minimize distance; Secondary: keep moving (avoid oscillation unless equal); Tertiary: deterministic.
        val = -(nd * 100 + (1 if (dx == 0 and dy == 0) else 0) * 5) + (curd - nd) * 2
        if val > best_step_val:
            best_step_val = val
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]