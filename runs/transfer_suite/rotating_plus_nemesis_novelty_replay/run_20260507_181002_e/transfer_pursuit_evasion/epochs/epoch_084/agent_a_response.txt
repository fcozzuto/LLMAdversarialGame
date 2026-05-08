def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "")) or ""
    is_evader = ("evad" in role.lower())

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        d = x1 - x2
        e = y1 - y2
        return (d if d >= 0 else -d) + (e if e >= 0 else -e)

    def boundary_pen(x, y):
        d = x
        if y < d: d = y
        r = (w - 1 - x)
        if r < d: d = r
        r = (h - 1 - y)
        if r < d: d = r
        return (2 if d <= 0 else 1 if d == 1 else 0)

    def adj_obs(x, y):
        c = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                if (x + ex, y + ey) in obstacles:
                    c += 1
        return c

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dx, best_dy = 0, 0
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = manh(nx, ny, ox, oy)
        wall = boundary_pen(nx, ny)
        ao = adj_obs(nx, ny)
        if is_evader:
            score = d * 10 - wall * 3 - ao * 2
        else:
            score = -d * 10 - wall * 2 - ao * 2
        if best_score is None or score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]