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
    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c
    role = (observation.get("self_role", "") or "").lower()
    self_is_pursuer = ("purs" in role) or (role == "")

    best_dx, best_dy = 0, 0
    if self_is_pursuer:
        best = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = dist(nx, ny, ox, oy)
            # Also prefer tighter space (less evader mobility) while staying close.
            wall = min(nx, ny, w - 1 - nx, h - 1 - ny)
            score = d * 100 - mobility(nx, ny) + wall
            if score < best:
                best = score
                best_dx, best_dy = dx, dy
    else:
        best = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist(nx, ny, ox, oy)
            wall = min(nx, ny, w - 1 - nx, h - 1 - ny)  # higher near edges
            # Flee while keeping options open; discourage moving into corners of obstacles via low mobility.
            score = d * 100 + mobility(nx, ny) * 5 + wall
            if score > best:
                best = score
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]