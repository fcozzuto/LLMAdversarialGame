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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                ob.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_key = None

    opp_dists_now = []
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if valid(rx, ry):
            opp_dists_now.append((md(ox, oy, rx, ry), rx, ry))
    opp_d_now_min = min([d for d, _, _ in opp_dists_now], default=10**9)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0

        my_best = 10**9
        opp_best = 10**9
        contest_bonus = 0
        immediate = 0
        center_bias = -abs(nx - cx) - abs(ny - cy)

        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry):
                continue
            dm_me = md(nx, ny, rx, ry)
            dm_opp = md(ox, oy, rx, ry)
            if dm_me < my_best:
                my_best = dm_me
            if dm_opp < opp_best:
                opp_best = dm_opp
            if dm_me == 0:
                immediate = 200  # hard prefer grabbing
            # contest: if I can be at/inside opponent's current reach for this resource
            dm_opp_now = md(ox, oy, rx, ry)
            if dm_me < dm_opp_now and dm_opp_now <= opp_d_now_min + 1:
                contest_bonus += (opp_d_now_min - dm_opp_now + 1) * 3

        # prefer moves that reduce my distance relative to opponent's best target distance
        score = (opp_best - my_best) * 5 + contest_bonus + immediate + center_bias * 0.2
        # deterministic tie-break: prefer non-stay, then lexicographic
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        key = (-score, stay_pen, dx, dy)

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]