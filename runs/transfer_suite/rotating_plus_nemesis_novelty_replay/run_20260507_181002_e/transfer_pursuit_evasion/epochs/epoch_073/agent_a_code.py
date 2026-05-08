def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def is_pursuer(role):
        s = str(role or "").lower()
        return ("pursuer" in s) or ("chaser" in s) or ("seeker" in s) or ("hunter" in s)

    self_p = is_pursuer(observation.get("self_role", ""))
    opp_p = is_pursuer(observation.get("opponent_role", ""))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if self_p and not opp_p:
        # Pursue opponent
        bestv = -10**18
        bestm = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -d2(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < bestm):
                bestv, bestm = v, (dx, dy)
        return [bestm[0], bestm[1]]

    if (not self_p) and opp_p:
        # Evade opponent
        bestv = -10**18
        bestm = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = d2(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < bestm):
                bestv, bestm = v, (dx, dy)
        return [bestm[0], bestm[1]]

    # Same type or unknown: keep distance if opponent is pursuer, else move toward
    target_is_purs = opp_p
    bestv = -10**18
    bestm = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = -d2(nx, ny, ox, oy) if target_is_purs else d2(nx, ny, ox, oy)
        if v > bestv or (v == bestv and (dx, dy) < bestm):
            bestv, bestm = v, (dx, dy)
    if legal(sx, sy):
        return [0, 0]
    return [bestm[0], bestm[1]]