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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    targetx, targety = far_corner

    # Score: pursuer minimizes distance; evader maximizes distance + edge pressure toward target corner
    # Also add small deterministic obstacle-avoidance via penalty for landing adjacent to obstacles.
    def obst_adj_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in blocked:
                    p += 1
        return p

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        edge = min(nx, ny, w - 1 - nx, h - 1 - ny)
        corner_drive = cheb(nx, ny, targetx, targety)
        score = 0
        if is_evader:
            # prefer moving away from pursuer; also progress toward far_corner (lower corner_drive is better)
            score = (d * 100) - (corner_drive * 3) + (edge * 1) - (obst_adj_pen(nx, ny) * 5)
        else:
            # prefer reducing distance; if tie, prefer moving toward far_corner away from self-corners to avoid getting blocked
            score = (-d * 100) + (corner_drive * 1) + (edge * 1) - (obst_adj_pen(nx, ny) * 5)
        # deterministic tie-break: fixed order by score then move components
        cand = (score, -dx, -dy) if is_evader else (score, dx, dy)
        if best is None or cand > best:
            best = cand
            best_move = [dx, dy]

    return best_move