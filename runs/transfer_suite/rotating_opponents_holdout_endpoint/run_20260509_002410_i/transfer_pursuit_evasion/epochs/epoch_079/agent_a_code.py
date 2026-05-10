def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = observation.get("self_role", "pursuer")
    is_pursuer = (self_role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best_dxdy = (0, 0)
    if is_pursuer:
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dist = d2(nx, ny, ox, oy)
            # Prefer capture (dist=0), then minimize distance; tie-break deterministically.
            key = (dist, abs(nx - ox), abs(ny - oy), -dx, -dy)
            if best_key is None or key < best_key:
                best_key = key
                best_dxdy = (dx, dy)
    else:
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dist = d2(nx, ny, ox, oy)
            # Avoid capture (dist=0) if possible; then maximize distance; tie-break.
            capture_penalty = 0 if dist == 0 else 1
            key = (-dist, -capture_penalty, -abs(nx - ox), -abs(ny - oy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]