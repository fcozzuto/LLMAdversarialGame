def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose nearest resource to us (deterministic tie-break)
    best_t = None
    best_d = 10**9
    for (tx, ty) in resources:
        d = cheb(sx, sy, tx, ty)
        if d < best_d or (d == best_d and (tx, ty) < best_t):
            best_d = d
            best_t = (tx, ty)
    tx, ty = best_t

    # Move one step toward target; tie-break by a fixed move ordering
    move_order = [(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    best_move = (0, 0)
    best_val = 10**9
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # primary: reduce distance to target; secondary: avoid moving away; tertiary: prefer staying when equal
        d = cheb(nx, ny, tx, ty)
        val = d * 100 + (0 if (dx, dy) == (0, 0) else 1)
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]