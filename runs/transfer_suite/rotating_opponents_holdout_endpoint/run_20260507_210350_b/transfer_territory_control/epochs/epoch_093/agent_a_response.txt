def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (7, 7))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, w - 1, h - 1

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    best_sc = -10**18
    best = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            sc = -10**12
        else:
            if (nx, ny) in opp_t:
                sc = 5000
            elif (nx, ny) in unclaimed:
                sc = 1200
            elif (nx, ny) in self_t:
                sc = 40
            else:
                sc = 60

            # Steal/contend: value cells adjacent to opponent territory.
            adj = 0
            for ax, ay in dirs:
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in opp_t:
                    adj += 1
            sc += adj * 260

            # Approach opponent to keep pressure (territory flipping on entry).
            d = man(nx, ny, ox, oy)
            sc += (80 - d) * 35

            # Slightly avoid moving farther from our own border when already near opponent.
            if opp_t:
                border_bias = 0
                for ax, ay in dirs:
                    tx, ty = nx + ax, ny + ay
                    if inb(tx, ty) and (tx, ty) in self_t:
                        border_bias += 1
                sc += border_bias * 8

            # Small tie-breaker: prefer not staying if a comparable steal exists.
            if dx == 0 and dy == 0:
                sc -= 3

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]