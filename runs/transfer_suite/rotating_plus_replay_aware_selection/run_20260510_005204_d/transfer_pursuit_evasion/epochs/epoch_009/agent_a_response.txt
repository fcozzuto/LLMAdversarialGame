def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    role = (observation.get("self_role") or "").lower()
    evader = ("evad" in role) or ("runner" in role) or ("escape" in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy)) if evader else (ox, oy)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to_op = cheb(nx, ny, ox, oy)
        d_to_target = cheb(nx, ny, tx, ty)
        # Evader: maximize distance to pursuer; small tiebreak toward farthest corner.
        # Pursuer: minimize distance to evader; small tiebreak toward evader position (same target).
        val = (-d_to_op, d_to_target) if evader else (d_to_op, d_to_target)
        if best_val is None or (val < best_val if not evader else val < best_val):
            best_val = val
            best_move = (dx, dy)
        elif best_val is not None:
            if evader:
                if val[0] < best_val[0] or (val[0] == best_val[0] and val[1] < best_val[1]):
                    best_val = val
                    best_move = (dx, dy)
            else:
                if val[0] < best_val[0] or (val[0] == best_val[0] and val[1] < best_val[1]):
                    best_val = val
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]