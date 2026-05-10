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
    opp_role = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evad" in role) or ("escape" in role) or ("run" in role) or ("hide" in role) or ("runner" in role)
    if not self_is_evader and (("evad" in opp_role) or ("escape" in opp_role) or ("run" in opp_role) or ("hide" in opp_role) or ("runner" in opp_role)):
        self_is_evader = True

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def cheb(x1, y1, x2, y2): 
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy
    def free_neighbors(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if ok(nx, ny):
                    c += 1
        return c

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny): 
            continue
        if nx == ox and ny == oy:
            score = -10**9 if self_is_evader else 10**9
        else:
            if self_is_evader:
                dist = md(nx, ny, ox, oy)
                mobility = free_neighbors(nx, ny)
                edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
                # Encourage distance, mobility, and avoid dead-corner confinement.
                score = dist * 10 + mobility * 3 - (1 if edge else 0) * 2 - (cheb(nx, ny, ox, oy) < md(sx, sy, ox, oy))
            else:
                dist = md(nx, ny, ox, oy)
                mobility = free_neighbors(nx, ny)
                score = -dist * 10 + mobility * 2
        if best is None or (score > best_score):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]