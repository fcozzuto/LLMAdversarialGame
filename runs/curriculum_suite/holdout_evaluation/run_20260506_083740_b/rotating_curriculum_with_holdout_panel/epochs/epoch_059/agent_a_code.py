def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        center = -(abs(nx - cx) + abs(ny - cy))
        best = -10**9
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry):
                continue
            dm_me = md(nx, ny, rx, ry)
            dm_opp = md(ox, oy, rx, ry)
            if dm_me == 0:
                score = 10**6 + 50 * center
            else:
                # Gain if we are closer than opponent; penalize if they are close.
                # Also create a "threat" by making opponent farther.
                lead = dm_opp - dm_me
                snap_pen = 1200 if dm_opp <= 2 and dm_me > dm_opp else (200 if dm_opp <= 3 else 0)
                score = 300 * lead - snap_pen - 2 * dm_me + 8 * center
            if score > best:
                best = score
        # Small tie-breaker toward moving along best resource direction deterministically
        # using opponent distance as secondary pressure.
        candidates.append((best, center, nx, ny, dx, dy))
    candidates.sort(reverse=True)
    return [int(candidates[0][4]), int(candidates[0][5])]