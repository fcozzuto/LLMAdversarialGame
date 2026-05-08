def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    role = (observation.get("self_role", "") or "").lower()
    escape = ("evader" in role) or ("escape" in role) or ("runner" in role)
    if ("pursuer" in role) or ("hunter" in role):
        escape = False
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))
    resources = observation.get("resources", []) or []
    rset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rset.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_score(nx, ny):
        if (nx, ny) in oset:
            return -10**9
        d = abs(nx - ox) + abs(ny - oy)
        s = -d if not escape else d
        if (nx, ny) in rset:
            s += 3
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (nx + ax, ny + ay) in oset:
                s -= 0.7
        return s

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            sc = best_score(nx, ny)
            if sc > best[0]:
                best = (sc, dx, dy)
    return [int(best[1]), int(best[2])]