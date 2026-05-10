def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("escape" in role) or ("hide" in role) or ("evader" in role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # Corner-bias for evasion; capture-bias for pursuer.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best = None
    best_val = -10**18 if is_evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_to_op = cheb(nx, ny, ox, oy)
        if is_evader:
            # Prefer increasing distance from opponent; also drift toward farthest corner.
            val = d_to_op * 1000 + cheb(nx, ny, target_corner[0], target_corner[1])
            if val > best_val:
                best_val, best = val, (dx, dy)
        else:
            # Prefer decreasing distance to opponent; slightly avoid hugging obstacles by preferring fewer illegal moves.
            illegal = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if not ok(tx, ty):
                    illegal += 1
            val = d_to_op * 1000 + illegal
            if val < best_val:
                best_val, best = val, (dx, dy)

    if best is None:
        # Deterministic fallback: stay if blocked everywhere.
        return [0, 0]
    return [best[0], best[1]]