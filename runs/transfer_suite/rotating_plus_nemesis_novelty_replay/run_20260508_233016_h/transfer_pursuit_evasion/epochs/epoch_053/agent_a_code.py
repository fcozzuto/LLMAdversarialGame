def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role) or ("flee" in role) or ("defender" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    tx, ty = far_corner

    def man(x, y):
        return abs(x - ox) + abs(y - oy)

    best = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = man(nx, ny)
        diag = 1 if (dx != 0 and dy != 0) else 0
        if is_evader:
            corner_term = - (abs(nx - tx) + abs(ny - ty))
            val = (d * 10.0) + (diag * 0.25) + corner_term
        else:
            # Pursuer: reduce distance; also bias toward moves that keep options open
            open_neighbors = 0
            for ddx, ddy in deltas:
                ax, ay = nx + ddx, ny + ddy
                if legal(ax, ay):
                    open_neighbors += 1
            val = (-d * 10.0) + (diag * 0.25) + (open_neighbors * 0.05)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    dx, dy = best
    if not (-1 <= dx <= 1 and -1 <= dy <= 1):
        return [0, 0]
    return [int(dx), int(dy)]