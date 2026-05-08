def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def clamp_moves(moves): return [m for m in moves if free(sx + m[0], sy + m[1])]
    self_role = (observation.get("self_role", "") or "").lower()
    evader = ("evader" in self_role) or ("runner" in self_role) or ("escape" in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = clamp_moves(moves)
    if not cand:
        return [0, 0]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = max(corners, key=lambda c: md(sx, sy, c[0], c[1])) if evader else (ox, oy)

    best = None
    best_score = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        d1 = md(nx, ny, ox, oy)
        dT = md(nx, ny, target[0], target[1])

        # local obstacle pressure: count blocked neighbors after move
        blocked = 0
        for ax, ay in moves:
            tx, ty = nx + ax, ny + ay
            if not inb(tx, ty) or (tx, ty) in obstacles:
                blocked += 1

        if evader:
            score = (d1, -dT, -blocked)  # maximize distance to pursuer; also drift toward corner
        else:
            score = (-d1, -dT, -blocked)  # minimize distance to evader; avoid tight areas

        if best is None or score > best_score:
            best, best_score = [dx, dy], score

    return [int(best[0]), int(best[1])]