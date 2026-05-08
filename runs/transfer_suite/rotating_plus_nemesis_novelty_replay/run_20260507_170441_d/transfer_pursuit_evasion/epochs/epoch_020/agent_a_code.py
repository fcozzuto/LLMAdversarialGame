def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    role = str(observation.get("self_role", "")).lower()
    evader = ("evad" in role) or ("escape" in role)

    if evader:
        tx, ty = corners[0]
        best = dist2(tx, ty, ox, oy)
        for cx, cy in corners[1:]:
            d = dist2(cx, cy, ox, oy)
            if d > best:
                best = d
                tx, ty = cx, cy
    else:
        tx, ty = ox, oy

    def obst_pen(x, y):
        if not obstacles:
            return 0
        m = 999
        for a, b in obstacles:
            d = abs(x - a) + abs(y - b)
            if d < m:
                m = d
        return 0 if m == 999 else m

    best_move = (0, 0)
    best_val = -10**18 if evader else 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, tx, ty)
        val = d + 0.01 * obst_pen(nx, ny) if evader else -d - 0.01 * obst_pen(nx, ny)
        if evader:
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            if val < best_val:
                best_val = val
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]