def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = observation.get("self_role", "pursuer")

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best_move = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        dist = cheb(nx, ny, ox, oy)

        # Small obstacle-aware term: avoid stepping near obstacles deterministically.
        near = 0
        for ox2, oy2 in blocked:
            if abs(nx - ox2) <= 1 and abs(ny - oy2) <= 1:
                near += 1
        near_term = 0.05 * near

        if role == "evader":
            val = dist + near_term + 0.001 * (dx * dx + dy * dy)
            better = (best_val is None) or (val > best_val)
        else:
            val = -dist + near_term - 0.001 * (dx * dx + dy * dy)
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move