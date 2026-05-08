def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) and ("evad" not in role)
    if not role:
        pursuer = True

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in oset

    def dist(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def greedy_toward(ax, ay, tx, ty):
        best = None
        best_d = 10**9
        for dx, dy in moves:
            nx, ny = ax + dx, ay + dy
            if not valid(nx, ny):
                continue
            d = dist(nx, ny, tx, ty)
            if d < best_d:
                best_d = d
                best = (nx, ny)
        if best is None:
            return (ax, ay)
        return best

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = dist(nx, ny, ox, oy)
        if pursuer:
            # Chase while avoiding dead mobility
            val = -d * 10.0 + mobility(nx, ny) * 0.2
        else:
            # Evade: maximize distance, avoid being captured next turn (model pursuer greedy)
            exp_opp = greedy_toward(ox, oy, nx, ny)
            captured_next = (exp_opp[0] == nx and exp_opp[1] == ny)
            val = d * 10.0 + mobility(nx, ny) * 0.2
            if captured_next:
                val -= 1000.0

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]