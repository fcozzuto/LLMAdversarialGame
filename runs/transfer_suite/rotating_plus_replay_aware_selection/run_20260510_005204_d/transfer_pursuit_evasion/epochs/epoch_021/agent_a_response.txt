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

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def best_corner_dist(x, y, targetx, targety):
        b = -1
        for cx, cy in corners:
            d = cheb(cx, cy, targetx, targety)
            if d > b:
                b = d
        return b

    best_move = (0, 0)
    best_score = None

    # Deterministic tie-break via fixed move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        e = edge_dist(nx, ny)
        corner_adv = best_corner_dist(nx, ny, ox, oy)

        # Small obstacle "repulsion": avoid stepping adjacent to any obstacle.
        adj = 0
        for (bx, by) in blocked:
            if cheb(nx, ny, bx, by) == 1:
                adj += 1

        if is_evader:
            score = (-d, -e, -corner_adv, -adj, dx, dy)
        else:
            # Pursuer: go closer; prefer edge/corner contact if it doesn't block.
            score = (d, -e, corner_adv, -adj, dx, dy)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]