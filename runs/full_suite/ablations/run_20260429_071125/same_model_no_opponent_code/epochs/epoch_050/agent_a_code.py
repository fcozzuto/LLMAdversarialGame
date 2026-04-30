def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def next_pos(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            return sx, sy
        return nx, ny

    # If we're somehow on invalid tile, move to any valid neighbor deterministically.
    if not inb(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose target deterministically: closest resource by chebyshev, tie by (x,y).
    tx, ty = None, None
    if resources:
        best = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            key = (d, rx, ry)
            if best is None or key < best:
                best = key
                tx, ty = rx, ry
    else:
        tx, ty = ox, oy  # no resources; just drift toward opponent

    best_move = [0, 0]
    best_score = None
    # Score: prefer reducing distance to target; small penalty for staying; avoid moving closer to opponent if tie.
    for dx, dy in moves:
        nx, ny = next_pos(dx, dy)
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        # Taking/approaching resources is covered by distance-to-target; add tiny deterministic tie-breakers.
        score = (-d_to_t, -d_to_o, -((nx - tx) * 0 + (ny - ty) * 0), -(dx == 0 and dy == 0), nx, ny, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx if inb(sx + dx, sy + dy) else 0, dy if inb(sx + dx, sy + dy) else 0]
            # If invalid move would be rejected, ensure return delta corresponds to engine behavior:
            if not inb(sx + dx, sy + dy):
                best_move = [0, 0]
    return [int(best_move[0]), int(best_move[1])]