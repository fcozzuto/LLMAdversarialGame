def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in blocked
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if "evad" in role:
        # Greedy escape: maximize distance to opponent; bias toward farthest corner.
        tc = max(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))
        tx, ty = tc[0], tc[1]
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            score = (dist2(nx, ny, ox, oy), dist2(nx, ny, tx, ty))
            if best is None or score > best[0]:
                best = (score, (dx, dy))
        if best is not None:
            return [int(best[1][0]), int(best[1][1])]
        return [0, 0]
    else:
        # Greedy chase: minimize distance to opponent; prefer moves that reduce both axes.
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            reduce = - (abs((nx - ox)) + abs((ny - oy)))
            # Extra bias: avoid stepping away if multiple equal distances.
            score = (d, -abs(dx) - abs(dy), -abs((nx - sx)) - abs((ny - sy)), reduce)
            if best is None or score < best[0]:
                best = (score, (dx, dy))
        if best is not None:
            return [int(best[1][0]), int(best[1][1])]
        return [0, 0]