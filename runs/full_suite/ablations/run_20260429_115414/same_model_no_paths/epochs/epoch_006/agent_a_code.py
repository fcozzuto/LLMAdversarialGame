def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def occ_pen(x, y):
        if not obstacles:
            return 0
        best = 999
        for px, py in obstacles:
            d = cheb(x, y, px, py)
            if d < best:
                best = d
        return 0 if best >= 2 else (4 - best)

    # Choose a target resource with a "race" bias and obstacle penalty.
    target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        dm = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If we are behind, bias toward resources where the opponent is *barely* ahead (smaller do-dm).
        # If we are ahead, bias toward the closest resource.
        lead = dm - do  # negative means we are closer
        key = (abs(lead), dm + occ_pen(rx, ry) - 0.25 * lead, dm)
        if best_key is None or key < best_key:
            best_key = key
            target = (rx, ry)

    # If no legal info, just move away from obstacles a bit.
    if not target:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            key = (occ_pen(nx, ny), cheb(nx, ny, ox, oy), nx, ny)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    tx, ty = target

    # Move evaluation: prefer reducing my distance to target; if opponent is closer, also prefer reducing their distance less.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dm = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # "race swing": we want dm < current dm, and if opponent is already closer, we want to minimize the gap.
        cur_dm = cheb(sx, sy, tx, ty)
        swing = (cur_dm - dm)  # positive if improving
        gap = dm - do  # negative if we are closer than opponent
        block_bonus = 0
        # If adjacent to target, strongly commit.
        if cheb(nx, ny, tx, ty) == 0:
            block_bonus = -50
        elif cheb(nx, ny, tx, ty) == 1:
            block_bonus = -15
        key = (dm, gap, -swing, occ_pen(nx, ny) + 0.1 * cheb(nx, ny, ox, oy), nx, ny)
        # Earlier ranks better; include a strong term when we can beat the opponent.
        if gap < 0:
            key = (key[0] - 2, key[1], key[2], key[3] + block_bonus, key[4], key[5])
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    return [best[1][0], best[1][1]]