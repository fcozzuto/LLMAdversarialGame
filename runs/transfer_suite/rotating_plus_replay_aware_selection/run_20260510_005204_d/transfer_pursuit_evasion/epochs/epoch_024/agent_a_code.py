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
    is_evader = ("evad" in role) or ("escape" in role) or ("run" in role) or ("hide" in role) or ("runner" in role)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break: prefer moves toward corners (evader) or toward opponent (pursuer), then lower dx/dy lexicographically.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if nx == ox and ny == oy:  # avoid immediate capture when acting as evader
            if is_evader:
                continue
        dist = cheb(nx, ny, ox, oy)
        if is_evader:
            corner_bonus = cheb(nx, ny, far_corner[0], far_corner[1]) * 0.01
            # maximize distance from opponent, then maximize corner progress
            score = dist + corner_bonus
            better = (best_score is None) or (score > best_score) or (score == best_score and (dx, dy) < best)
        else:
            # pursuer minimizes distance; small bias to avoid obstacles adjacency by preferring moves with more "free" neighbors
            free = 0
            for adx, ady in moves:
                tx, ty = nx + adx, ny + ady
                if ok(tx, ty):
                    free += 1
            score = -dist + free * 0.001
            better = (best_score is None) or (score > best_score) or (score == best_score and (dx, dy) < best)
        if better:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]