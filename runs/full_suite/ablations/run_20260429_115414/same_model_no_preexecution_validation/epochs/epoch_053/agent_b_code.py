def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a contested target where we are (or can become) closer than opponent.
    best_tx, best_ty = resources[0]
    best = None
    for tx, ty in resources:
        d_me = cheb(sx, sy, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        lead = d_op - d_me  # positive => we are closer
        # Prefer larger lead; if tie, prefer smaller our distance; then prefer farther from opponent (more contested)
        key = (lead, -d_op, -d_me)
        if best is None or key > best:
            best = key
            best_tx, best_ty = tx, ty

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Move greedily toward target, but discourage steps that let opponent get significantly closer to same target.
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me2 = cheb(nx, ny, best_tx, best_ty)
        d_op2 = cheb(ox, oy, best_tx, best_ty)
        # Opponent "pressure" if our move doesn't reduce distance much while it stays competitive
        # Use integer scoring via tuples.
        improve = cheb(sx, sy, best_tx, best_ty) - d_me2
        lead_now = d_op2 - d_me2
        # Prefer: higher lead_now, then higher improve, then lower d_me2, then keep closer to center slightly
        cx = (w - 1) // 2
        cy = (h - 1) // 2
        center_pen = cheb(nx, ny, cx, cy)
        score = (lead_now, improve, -d_me2, -center_pen)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move