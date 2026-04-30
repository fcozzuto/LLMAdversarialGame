def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    occ = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                occ.add((px, py))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in occ:
                resources.append((rx, ry))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    deltas.sort()

    if not resources:
        best = (-10**18, (0, 0))
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            v = -(man(nx, ny, ox, oy))
            if v > best[0]:
                best = (v, (dx, dy))
        return [best[1][0], best[1][1]]

    # Choose a target resource that maximizes our advantage (we get there sooner or deny opponent).
    best_t = None
    best_adv = -10**18
    for rx, ry in resources:
        d_me = man(x, y, rx, ry)
        d_op = man(ox, oy, rx, ry)
        # Prefer resources where we're closer; also prefer slightly farther if we already can deny.
        adv = (d_op - d_me) * 100 - d_me
        if adv > best_adv:
            best_adv = adv
            best_t = (rx, ry)

    rx, ry = best_t
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        d_me = man(nx, ny, rx, ry)
        d_op = man(ox, oy, rx, ry)

        # Secondary targets: if target is blocked by opponent, consider closest resource.
        alt_min = 10**9
        for arx, ary in resources:
            alt_min = min(alt_min, man(nx, ny, arx, ary))

        # Deny opponent: discourage moves that make them closer to the current target than us.
        deny = 0
        if man(ox, oy, rx, ry) < d_me:
            deny = (d_me - man(ox, oy, rx, ry)) * 50

        # Obstacle/edge safety: keep some distance from obstacles (local penalty).
        local_pen = 0
        for sx in (-1, 0, 1):
            for sy in (-1, 0, 1):
                if sx == 0 and sy == 0:
                    continue
                px, py = nx + sx, ny + sy
                if (px, py) in occ:
                    local_pen += 1

        score = -d_me * 10 - alt_min + deny - local_pen * 2 - (d_op - d_me < 0) * 200
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]