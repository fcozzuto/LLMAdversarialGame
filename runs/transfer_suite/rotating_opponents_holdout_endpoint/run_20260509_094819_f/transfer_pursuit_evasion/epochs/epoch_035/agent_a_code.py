def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    role = ((observation.get("self_role", "") or "") + " " + (observation.get("environment_name", "") or "")).lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("escape" in role) or ("evasion" in role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    best = None  # (key, dx, dy) where higher is better for evader
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        if (not is_evader) and dist == 0:
            return [dx, dy]

        mob = mobility(nx, ny)
        wall_pen = 0
        if nx == 0 or nx == w - 1: wall_pen += 1
        if ny == 0 or ny == h - 1: wall_pen += 1
        # deterministic tie-break: prefer earlier moves in list by using dx,dy in key
        if is_evader:
            score = dist * 10 + mob - 2 * wall_pen
        else:
            score = -dist * 10 + mob - 2 * wall_pen

        cand = (score, -dx, -dy)  # stable tie-break using dx/dy
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    # recover dx,dy from tie-break components
    # best is (score, -dx, -dy)
    return [-best[1], -best[2]]