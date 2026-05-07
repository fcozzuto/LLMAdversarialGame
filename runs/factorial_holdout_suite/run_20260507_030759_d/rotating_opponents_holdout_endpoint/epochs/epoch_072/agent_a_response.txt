def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = None
    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        x, y = r[0], r[1]
        if not (isinstance(x, int) and isinstance(y, int) and inb(x, y)):
            continue
        md = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # Prefer resources where we have a (strict) distance advantage; otherwise closest.
        score = (od - md, -md, x, y)  # maximize od-md, then minimize md via -md
        if best is None or score > best:
            best = score
            target = (x, y)

    if target is None:
        # fallback: avoid obstacles; move to maximize distance from opponent and stay safe
        best_step = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny):
                    val = (cheb(nx, ny, ox, oy), -cheb(nx, ny, sx, sy))
                    if best_step is None or val > best_step:
                        best_step = val
                        move = [dx, dy]
        return move if best_step is not None else [0, 0]

    tx, ty = target
    best_move = None
    move = [0, 0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            # Tie-break: also prefer moves where opponent is farther from the target.
            od = cheb(ox, oy, tx, ty)
            val = (-d, od, -abs(nx - tx) - abs(ny - ty), dx, dy)
            if best_move is None or val > best_move:
                best_move = val
                move = [dx, dy]
    return move