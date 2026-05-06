def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

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

    res_cells = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                res_cells.append((x, y))

    if not res_cells:
        best = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            val = -md(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Advantage: how much closer we are than the opponent (bigger is better).
        best_adv = -10**18
        for rx, ry in res_cells:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            # slight preference for nearer resources to avoid dithering
            adv -= 0.05 * sd
            if adv > best_adv:
                best_adv = adv

        # Also discourage stepping toward the opponent (helps vs row sweeping).
        opp_pen = 0.02 * md(nx, ny, ox, oy)
        val = best_adv - opp_pen

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]