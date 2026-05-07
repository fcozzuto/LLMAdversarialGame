def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

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

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not valid(nx, ny):
            continue

        local_best = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if nx == rx and ny == ry:
                val = 10**9
            else:
                lead = od - sd
                val = lead * 200 - sd - (sd == 0) * 1000
            if val > local_best:
                local_best = val

        # tie-break toward quicker collection
        if local_best > best_val:
            best_val = local_best
            best = (dx, dy)
        elif local_best == best_val:
            # deterministic preference: smaller distance to best resource from next
            cand_sd = min(man(nx, ny, rx, ry) for rx, ry in resources)
            best_dx, best_dy = best
            bx, by = int(sx + best_dx), int(sy + best_dy)
            best_sd = min(man(bx, by, rx, ry) for rx, ry in resources)
            if cand_sd < best_sd:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]