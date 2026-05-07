def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def target_score(nx, ny, tx, ty):
        ds = man(nx, ny, tx, ty)
        do = man(ox, oy, tx, ty)
        # Prefer resources where we are strictly closer (or the opponent is farther).
        # Small bias toward shorter self distance to finish quickly.
        return (do - ds) * 100 - ds

    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            # Choose the best target for this candidate move (deterministic).
            best_tk = None
            for tx, ty in resources:
                tk = target_score(nx, ny, tx, ty)
                # Tie-break deterministically by target coordinates.
                key = (tk, -man(nx, ny, tx, ty), -man(ox, oy, tx, ty), ty, tx)
                if best_tk is None or key > best_tk:
                    best_tk = key
            # Also tie-break by opponent distance after move to reduce denier impact.
            key2 = (best_tk[0], best_tk[1], best_tk[2], -man(nx, ny, ox, oy), dy, dx)
        else:
            # No visible resources: head toward nearest corner away from opponent line.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            ck = None
            for cx, cy in corners:
                if (cx, cy) in blocked:
                    continue
                ds = man(nx, ny, cx, cy)
                do = man(ox, oy, cx, cy)
                key = ((do - ds) * 10 - ds, cy, cx)
                if ck is None or key > ck:
                    ck = key
            key2 = (ck[0], -man(nx, ny, ox, oy), dy, dx)
        if best_key is None or key2 > best_key:
            best_key = key2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]