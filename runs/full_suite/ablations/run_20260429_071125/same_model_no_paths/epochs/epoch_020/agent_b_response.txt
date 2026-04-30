def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not valid(sx, sy):
        for dx, dy in moves:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        if valid(sx + dx, sy + dy):
            return [dx, dy]
        for ddx, ddy in moves:
            if valid(sx + ddx, sy + ddy):
                return [ddx, ddy]
        return [0, 0]

    # Target resources where we have the strongest distance advantage over opponent
    best = None
    bestkey = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer larger advantage, then closer self, then deterministic coordinate tie-break
        key = (do - ds, -ds, -rx, -ry)
        if bestkey is None or key > bestkey:
            bestkey = key
            best = (rx, ry)

    rx, ry = best

    # Greedy one-step improvement toward target, with opponent pressure and obstacle penalty
    bestmove = [0, 0]
    bestscore = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_next = man(nx, ny, rx, ry)
        # Opponent tends to steal: penalize getting too close to opponent without reaching target
        do_next = man(ox, oy, rx, ry)
        opp_dist = man(nx, ny, ox, oy)
        score = (do_next - ds_next) * 10 - ds_next
        score += 0.5 * opp_dist  # keep away slightly
        # Small preference for moving in correct general direction deterministically
        score += 0.01 * (abs(nx - rx) < abs(sx - rx) or abs(ny - ry) < abs(sy - ry))
        if score > bestscore:
            bestscore = score
            bestmove = [dx, dy]

    return bestmove