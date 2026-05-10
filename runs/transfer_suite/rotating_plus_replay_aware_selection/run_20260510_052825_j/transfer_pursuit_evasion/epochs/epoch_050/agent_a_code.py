def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in self_role) or (self_role == "evader") or ("purs" in opponent_role) or ("purs" not in self_role and "purs" in opponent_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def obst_pen(nx, ny):
        if (nx, ny) in obstacles: return 999
        p = 0
        for dx, dy in neigh:
            if (nx + dx, ny + dy) in obstacles:
                p += 1
        return p

    # Evader targets the farthest corner not "overcrowded" by obstacles; pursuer just improves distance.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = None
    best_corner_score = None
    for cx, cy in corners:
        cpen = obst_pen(cx, cy)
        if cpen >= 999: 
            continue
        score = man(cx, cy, ox, oy) - 0.8 * cpen
        if best_corner_score is None or score > best_corner_score:
            best_corner_score = score
            target_corner = (cx, cy)
    if target_corner is None:
        target_corner = max(corners, key=lambda c: man(c[0], c[1], ox, oy))

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        p = obst_pen(nx, ny)
        if p >= 999:
            continue

        if self_is_evader:
            dist = man(nx, ny, ox, oy)
            corner_dist = man(nx, ny, target_corner[0], target_corner[1])
            val = 1.15 * dist + 0.35 * (-corner_dist) - 0.9 * p
        else:
            dist = man(nx, ny, ox, oy)
            val = -1.25 * dist - 0.9 * p

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]