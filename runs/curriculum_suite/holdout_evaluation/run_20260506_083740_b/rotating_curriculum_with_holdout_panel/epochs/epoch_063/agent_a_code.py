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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                nx, ny, dx, dy = sx, sy, 0, 0
            score = (md(nx, ny, cx, cy), md(nx, ny, ox, oy))
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    def move_value(nx, ny):
        best_adv = None
        best_me_dist = None
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not inb(rx, ry) or (rx, ry) in ob:
                continue
            dme = md(nx, ny, rx, ry)
            dop = md(ox, oy, rx, ry)
            adv = dme - dop  # negative means we are closer
            key = (adv, dme)
            if best_adv is None or key < (best_adv, best_me_dist):
                best_adv, best_me_dist = adv, dme
        if best_adv is None:
            best_adv, best_me_dist = 0, 10**9

        # If opponent is currently much closer everywhere, prioritize creating separation
        dop_min = min(md(ox, oy, int(r[0]), int(r[1])) for r in resources if r and len(r) >= 2 and inb(int(r[0]), int(r[1])) and (int(r[0]), int(r[1])) not in ob)
        sep = md(nx, ny, ox, oy)

        center = -(abs(nx - cx) + abs(ny - cy))
        # Tie-break: prefer moves that don't hand the nearest resource to opponent too strongly
        return (best_adv, best_me_dist, dop_min - sep, -center)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0
        val = move_value(nx, ny)
        if best is None or val < best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]] if best else [0, 0]