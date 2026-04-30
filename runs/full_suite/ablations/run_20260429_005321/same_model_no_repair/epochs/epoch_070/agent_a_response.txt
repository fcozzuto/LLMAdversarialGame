def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def occ_pen(x, y):
        if (x, y) in obst: return 10**6
        return 0

    def near_pen(x, y):
        # discourage moving adjacent to obstacles (safer corridors)
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obst:
                    p += 2
        return p

    def score_target(rx, ry):
        if (rx, ry) in obst: 
            return -10**12
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # primary: maximize advantage (opp closer => worse). Favor states where we are closer.
        adv = do - ds
        # secondary: quick pickup if advantage similar
        t = -ds
        # tertiary: avoid dead-ends by choosing resources with fewer nearby obstacles
        np = -near_pen(rx, ry)
        # slight center bias
        cb = - (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
        return (adv * 1000 + t * 10 + np + cb)

    # If no resources, drift toward opponent's side while avoiding obstacles
    if not resources:
        tx, ty = (w - 1 - ox, h - 1 - oy)
        best = (-10**12, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            key = -occ_pen(nx, ny) + (-cheb(nx, ny, tx, ty)) - near_pen(nx, ny)
            if key > best[0]:
                best = (key, dx, dy)
        return [int(best[1]), int(best[2])]

    # Choose target with maximum advantage
    best_key = -10**18
    tx, ty = resources[0][0], resources[0][1]
    for rx, ry in resources:
        k = score_target(rx, ry)
        if k > best_key:
            best_key = k
            tx, ty = rx, ry

    # Greedy move: maximize next-state objective relative to chosen target
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # If we move closer while keeping/creating advantage, prefer it
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        adv_next = no - ns
        val = adv_next * 1000 - ns * 10 - occ_pen(nx, ny) - near_pen(nx, ny)
        if val > best[0]:
            best = (val, dx, dy)

    # Fallback deterministic: stay if something odd
    if best[0] <= -10**17:
        return [0, 0]
    return [int(best[1]), int(best[2])]