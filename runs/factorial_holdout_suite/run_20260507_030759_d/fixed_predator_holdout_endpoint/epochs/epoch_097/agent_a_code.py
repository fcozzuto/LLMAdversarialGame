def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick best target: maximize advantage over opponent, then prefer closer.
    best = None
    best_key = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        key = (do - ds, -ds)  # bigger advantage; if tie, closer
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    # Greedy one-step: consider all moves (incl stay), avoid obstacles, maximize margin improvement.
    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            deltas.append((dx, dy))
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Prefer moves that reduce our distance to target; also prefer increasing relative lead.
        lead = no - ns
        # Small tie-break: avoid drifting away from target.
        key = (lead, -ns, -abs(nx - sx) - abs(ny - sy))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]