def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in blocked:
                c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    d0 = cheb(sx, sy, ox, oy)

    best_move = (0, 0)
    best_sc = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        d1 = cheb(nx, ny, ox, oy)
        fn = free_neighbors(nx, ny)
        corner_max = 0
        for cx, cy in corners:
            dd = cheb(nx, ny, cx, cy)
            if dd > corner_max:
                corner_max = dd

        if is_evader:
            # Prefer increasing distance; bias to corners; avoid reducing distance too much.
            delta = d1 - d0
            sc = (d1 * 10.0) + (corner_max * 0.5) + (fn * 0.05)
            if delta < 0:
                sc += delta * 2.0  # discourage getting closer
        else:
            # Pursuer: greedy distance minimization with obstacle-aware tie-break.
            sc = (-d1 * 10.0) + (fn * 0.05)
            if d1 == 0:
                sc += 1000.0

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]