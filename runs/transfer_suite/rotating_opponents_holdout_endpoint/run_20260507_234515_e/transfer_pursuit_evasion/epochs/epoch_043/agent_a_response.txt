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
    def neigh_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c
    def wall_score(x, y): return min(x, y, w - 1 - x, h - 1 - y)  # center-low, edge-high

    role = (observation.get("self_role", "") or "").lower()
    self_is_pursuer = ("purs" in role) or (role == "")

    best = None
    best_key = None

    # Evader uses a deterministic corner target that maximizes distance from pursuer.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if not self_is_pursuer:
        tx, ty = max(corners, key=lambda c: md(c[0], c[1], ox, oy))
    else:
        tx, ty = ox, oy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = md(nx, ny, ox, oy)
        d_target = md(nx, ny, tx, ty)
        # Primary: for pursuer minimize distance to opponent; for evader maximize it.
        primary = -d_opp if self_is_pursuer else d_opp
        # Secondary: avoid dead-ends; tertiary: bias toward being on edges for pursuer, toward center for evader.
        sec = neigh_count(nx, ny)
        ter = wall_score(nx, ny)
        key = (primary, sec, ter)
        if best_key is None or key > best_key:
            best_key, best = key, (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]