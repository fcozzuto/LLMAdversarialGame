def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in self_role) or (self_role == "pursuer")

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target_corner = corners[0]
    if not pursuer:
        best = None
        for c in corners:
            if c in blocked:
                continue
            d = cheb(c[0], c[1], ox, oy)
            if best is None or d > best:
                best = d
                target_corner = c

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        dist_op = cheb(nx, ny, ox, oy)
        if pursuer:
            dist_corner = cheb(nx, ny, target_corner[0], target_corner[1])
            score = -dist_op * 100 - dist_corner
        else:
            dist_corner = cheb(nx, ny, target_corner[0], target_corner[1])
            score = dist_op * 100 + dist_corner

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]