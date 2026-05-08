def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs

    unclaimed = set()
    for c in (observation.get("unclaimed_cells") or []):
        if c is not None and len(c) >= 2:
            unclaimed.add((int(c[0]), int(c[1])))

    opp_t = set()
    for c in (observation.get("opponent_territory") or []):
        if c is not None and len(c) >= 2:
            opp_t.add((int(c[0]), int(c[1])))

    targets = []
    for r in (observation.get("resources") or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y) and (x, y) != (ox, oy):
                targets.append((x, y))
    if not targets:
        for c in unclaimed:
            if free(c[0], c[1]) and c != (ox, oy):
                targets.append(c)

    if not targets:
        targets = [(ox, oy)]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    cxands = [(sx, sy)]
    best = (0, 0)
    best_sc = -10**18

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            continue
        if (nx, ny) in opp_t:
            sc = -10**9
        else:
            t = min(targets, key=lambda p: md(nx, ny, p[0], p[1]))
            sc = -md(nx, ny, t[0], t[1])
            if (nx, ny) in unclaimed:
                sc += 3
            sc -= 0.001 * md(nx, ny, w // 2, h // 2)
            sc += -0.3 * md(nx, ny, ox, oy)
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]