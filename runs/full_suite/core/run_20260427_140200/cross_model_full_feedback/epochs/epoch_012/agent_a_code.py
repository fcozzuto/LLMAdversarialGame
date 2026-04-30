def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick best resource by deterministic advantage heuristic
    target = None
    bestv = -10**18
    for rx, ry in resources:
        d_me = man(sx, sy, rx, ry)
        d_op = man(ox, oy, rx, ry)
        # High when we are closer than opponent; slight tie-break toward nearer resources
        v = (d_op - d_me) * 1000 - (d_me) * 3 - (rx * 0.001 + ry * 0.001)
        if v > bestv:
            bestv = v
            target = (rx, ry)

    # If no resources, drift toward center while avoiding opponent
    if target is None:
        target = (w // 2, h // 2)

    tx, ty = target
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d_nt = man(nx, ny, tx, ty)
        d_ot = man(ox, oy, tx, ty)
        # Encourage closing on target relative to opponent
        rel_gain = (d_ot - d_nt) * 20

        d_no = man(nx, ny, ox, oy)
        d_so = man(sx, sy, ox, oy)
        # If opponent closer to target, prioritize distancing from opponent; else stay cohesive
        opp_pressure = man(ox, oy, tx, ty) - man(sx, sy, tx, ty)
        sep = d_no * (2 if opp_pressure > 0 else 1)

        # Small preference for reducing distance overall and slight center bias
        center_bias = -abs((nx - (w - 1) / 2)) - abs((ny - (h - 1) / 2))
        score = rel_gain + sep - d_nt * 2 + center_bias * 0.1

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move