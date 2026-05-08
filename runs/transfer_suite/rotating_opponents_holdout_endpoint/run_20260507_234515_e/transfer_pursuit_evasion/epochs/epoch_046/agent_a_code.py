def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in oset
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or (role == "")
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    best_score = None
    best_move = (0, 0)

    if pursuer:
        # Pursuer: minimize distance to opponent; break ties by higher mobility; prefer not moving into low-mobility corridors.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            dist = md(nx, ny, ox, oy)
            mob = mobility(nx, ny)
            # small bonus for staying nearer to center-ish (reduces getting trapped by wall-running)
            center_bonus = -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * 0.01
            score = (-dist * 1000) + (mob * 2) + center_bonus
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # Evader: maximize distance to opponent; avoid reducing mobility; if possible, drift toward the farthest reachable corner.
        target_corner = max(corners, key=lambda c: md(c[0], c[1], ox, oy))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = md(nx, ny, ox, oy)
            mob = mobility(nx, ny)
            corner_dist = md(nx, ny, target_corner[0], target_corner[1])
            # Prefer being far from opponent; in ties, prefer higher mobility and closer-to-corner progress.
            score = (dist * 1000) + (mob * 2) + (-corner_dist * 0.5)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]