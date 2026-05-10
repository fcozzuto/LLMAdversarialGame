def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    blocked = {(int(p[0]), int(p[1])) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

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

    # Deterministic tie-breaking order: prefer staying still if score equal by scanning moves list.
    best = None
    best_val = None

    if evader:
        # Flee opponent; also bias toward farthest corner from opponent to avoid oscillations.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_corner = cheb(nx, ny, tx, ty)
            val = (d_opp * 1000) + d_corner
            if best is None or val > best_val:
                best = (dx, dy)
                best_val = val
    else:
        # Pursue opponent greedily; avoid obstacles; if blocked, move to reduce distance to escape corner.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], sx, sy))  # deterministic "anchor"
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_anchor = cheb(nx, ny, tx, ty)
            val = (-d_opp * 1000) + (-d_anchor * 0)  # anchor term neutral but keeps structure simple
            if best is None or val > best_val:
                best = (dx, dy)
                best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]