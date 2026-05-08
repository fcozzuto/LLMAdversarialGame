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

    def dist(x, y, tx, ty):
        return abs(x - tx) + abs(y - ty)

    best = None
    best_val = -10**18 if pursuer else 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist(nx, ny, ox, oy)
        val = d if not pursuer else -d
        if best is None:
            best = [dx, dy]
            best_val = val
        else:
            if val > best_val if pursuer else val < best_val:
                best_val = val
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best