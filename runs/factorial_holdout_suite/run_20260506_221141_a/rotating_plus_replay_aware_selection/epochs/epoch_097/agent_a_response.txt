def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def drift_target():
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best, bestv = [0, 0], -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            # Prefer not being stuck and moving generally toward target
            v = -d - (1 if (nx, ny) in obstacles else 0)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    if not resources:
        return drift_target()

    best_move, best_val = [0, 0], -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Score this move by best resource we can contest next
        move_val = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            ahead = opd - myd  # positive if we arrive earlier (or equal if 0)
            # Extra bias if we can "immediately" be on a resource
            imm = 1 if myd == 0 else 0
            # Discourage very long detours and prefer resources closer overall
            v = ahead * 10 + imm * 100 - myd
            if v > move_val:
                move_val = v
        # Mild tie-break: prefer moves that also reduce distance to any resource
        if move_val > best_val:
            best_val = move_val
            best_move = [dx, dy]

    return best_move