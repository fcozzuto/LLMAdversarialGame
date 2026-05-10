def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("escape" in role) or ("hide" in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        if is_evader:
            df = cheb(nx, ny, far_corner[0], far_corner[1])
            dn = cheb(nx, ny, near_corner[0], near_corner[1])
            val = 10.0 * d - 0.7 * df - 0.3 * dn
            # slight tie-break toward staying away from board edges to reduce wall-running
            val += 0.01 * min(nx, w - 1 - nx) + 0.01 * min(ny, h - 1 - ny)
            better = (best_val is None) or (val > best_val)
        else:
            dc = cheb(nx, ny, ox, oy)
            val = -dc
            # prefer pushing toward evader's far corner if possible; also avoid giving distance back
            push = cheb(nx, ny, far_corner[0], far_corner[1])
            val -= 0.05 * push
            # prefer staying within open area (avoid tight boundaries if obstacle-free is unknown)
            val += 0.01 * min(nx, w - 1 - nx) + 0.01 * min(ny, h - 1 - ny)
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best