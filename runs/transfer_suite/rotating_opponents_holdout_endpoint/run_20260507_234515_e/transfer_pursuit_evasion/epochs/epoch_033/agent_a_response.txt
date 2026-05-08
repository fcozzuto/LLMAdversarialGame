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

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("direct" in role and "evad" not in role) or (role == "")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_move(nx, ny):
        # obstacle/outside heavily penalize
        if not inside(nx, ny) or (nx, ny) in oset:
            return 10**9
        dx = abs(nx - ox)
        dy = abs(ny - oy)
        dist = dx + dy
        # pursue: minimize distance; evade: maximize distance (and slightly avoid staying)
        if pursuer:
            return dist * 10 + (1 if (nx == sx and ny == sy) else 0)
        else:
            return (-dist) * 10 + (0 if (nx != sx or ny != sy) else 1)

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = score_move(nx, ny)
        if best_sc is None or sc < best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]