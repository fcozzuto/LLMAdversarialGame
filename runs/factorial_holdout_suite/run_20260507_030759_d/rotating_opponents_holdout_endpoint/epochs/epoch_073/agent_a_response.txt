def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def best_moves(x, y, tx, ty):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        candidates = []
        # Prefer diagonal; then axis; then stay.
        candidates.append((dx, dy))
        candidates.append((dx, 0))
        candidates.append((0, dy))
        candidates.append((0, 0))
        # Fallback: any valid adjacent move that reduces our distance to target.
        curd = cheb(x, y, tx, ty)
        if not any(inb(x + a, y + b) for a, b in candidates):
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    if a == 0 and b == 0:
                        continue
                    nx, ny = x + a, y + b
                    if inb(nx, ny):
                        if cheb(nx, ny, tx, ty) <= curd:
                            candidates.append((a, b))
        for a, b in candidates:
            if inb(x + a, y + b):
                return [a, b]
        return [0, 0]

    target = None
    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        x, y = r[0], r[1]
        if not (isinstance(x, int) and isinstance(y, int) and inb(x, y)):
            continue
        ts = cheb(sx, sy, x, y)
        to = manh(ox, oy, x, y)  # opponent likely uses Manhattan-like chase
        # Materially different selection: prioritize earliest self arrival; require opponent not too close.
        margin = to - ts
        score = (ts, -max(0, margin), -x, -y)  # earlier self first; then maximize safe lead
        if best is None or score < best:
            best = score
            target = (x, y)

    if target is None:
        return [0, 0]
    return best_moves(sx, sy, target[0], target[1])