def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((a, b) for a, b in obstacles)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        da = abs(ax - bx)
        db = abs(ay - by)
        return da if da > db else db

    if not resources:
        best = (0, 0)
        best_val = -10**9
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacle_set:
                continue
            val = cheb(nx, ny, ox, oy)
            if val > best_val or (val == best_val and (dx, dy) < best):
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]]

    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # prioritize denying: larger (od-sd), then smaller sd, then stable resource tie
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    cand = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacle_set:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)  # static during this move
        # maximize denial pressure while also moving toward target; deterministic tie
        key = (nod - nsd, -nsd, dx, dy)
        cand.append((key, (dx, dy)))
    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: t[0], reverse=True)
    return [cand[0][1][0], cand[0][1][1]]