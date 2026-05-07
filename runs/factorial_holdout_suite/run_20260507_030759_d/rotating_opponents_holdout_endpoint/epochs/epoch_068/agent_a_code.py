def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid_cell(x, y):
        return inb(x, y) and (x, y) not in blocked

    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = opp_pos[0], opp_pos[1]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid_res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and valid_cell(x, y):
                valid_res.append((x, y))

    if not valid_res:
        for dx, dy in [(0, 0), (0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = sx + dx, sy + dy
            if valid_cell(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    best_key = None
    for x, y in valid_res:
        myd = cheb(sx, sy, x, y)
        opd = cheb(ox, oy, x, y)
        # Prefer resources we're closer to; otherwise still take one that our move can improve on.
        key = (opd - myd, -myd, -x, -y)
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid_cell(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Also avoid stepping into opponent's immediate threat region (coarse).
        opp_th = cheb(ox, oy, nx, ny)
        val = (-d, opp_th)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]