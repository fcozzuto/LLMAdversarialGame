def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        if resources:
            cur = min(man(sx, sy, rx, ry) for rx, ry in resources)
            nxt = min(man(nx, ny, rx, ry) for rx, ry in resources)
            gain = cur - nxt
        else:
            gain = 0

        opp_cur = man(sx, sy, ox, oy)
        opp_nxt = man(nx, ny, ox, oy)
        # Prefer reducing opponent distance when no resources, otherwise small preference for safety.
        adv = (opp_cur - opp_nxt) if not resources else -(opp_nxt)

        val = gain * 1000 + adv
        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0] if inside(sx, sy) else [0, 0]