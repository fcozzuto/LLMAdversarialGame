def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not inside(sx, sy):
        for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]:
            if inside(sx + dx, sy + dy):
                sx, sy = sx + dx, sy + dy
                break

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def neighbor_block_density(x, y):
        k = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
                k += 1
        return k

    best_move = (0, 0)
    best_score = -10**9
    # Strategic switch: prioritize resources where we gain time advantage over opponent; otherwise drift to "high contest" areas.
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inside(nx, ny):
            continue
        score = -0.2 * neighbor_block_density(nx, ny)  # avoid trapped/blocked zones
        if resources:
            for tx, ty in resources:
                ds = man(nx, ny, tx, ty)
                do = man(ox, oy, tx, ty)
                # advantage: larger when we can arrive sooner than opponent (or at least not slower)
                adv = (do - ds)
                # prefer closer overall after accounting for advantage
                proximity = -0.08 * ds
                # tie-break toward staying on the side of the map opposite the opponent
                spread = (abs((nx + ny) - (ox + oy)) % (w + h)) * 0.0
                score += 1.7 * adv + proximity + spread
        else:
            # no resources visible: move toward center-ish to reduce being outflanked deterministically
            score += -(abs((nx - (w-1)/2)) + abs((ny - (h-1)/2))) * 0.3

        if score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]