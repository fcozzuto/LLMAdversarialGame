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

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("run" in role) or ("escape" in role) or ("hide" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    # Favor contact or evasion in a corner/edge-safe way; deterministic tie-break via fixed move order.
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        e = edge_dist(nx, ny)

        # Pursuer: minimize distance to opponent; Evader: maximize distance and keep away from edges only slightly.
        if is_evader:
            val = (d * 1000) + (e * 3)
            better = (best_val is None) or (val > best_val)
        else:
            val = (-d * 1000) + (e * 1)
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best = [dx, dy]

    if best is None:
        # No legal move found (unlikely): stay.
        return [0, 0]
    return [int(best[0]), int(best[1])]