def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_raw) if obstacles_raw else set()

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # No resources: try to reduce distance to opponent corner-capture is irrelevant; just drift toward center safely.
        cx, cy = (w // 2), (h // 2)
        best = [0, 0]
        best_d = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, cx, cy)
            if best_d is None or d < best_d:
                best_d = d
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer resources where we can arrive not later than opponent.
        # Tie-break: maximize opponent advantage gap after our move (more negative means we are closer),
        # then prioritize smaller our distance; then deterministic coordinate preference.
        best_for_this_move = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)

            # Primary: (od - md) so positive means we are closer/equal than opponent.
            # Secondary: -md (smaller md better).
            # Tertiary: pick a consistent resource order.
            cand = (od - md, -md, -rx, -ry)
            if best_for_this_move is None or cand > best_for_this_move:
                best_for_this_move = cand

        # Small extra: avoid stepping into "trap" near obstacles by penalizing proximity.
        if best_for_this_move is None:
            continue
        trap_pen = 0
        for oxp, oyp in obstacles:
            # Chebyshev proximity penalty within 1
            if cheb(nx, ny, oxp, oyp) <= 1:
                trap_pen += 1

        val = (best_for_this_move[0], best_for_this_move[1], best_for_this_move[2], best_for_this_move[3], -trap_pen)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move