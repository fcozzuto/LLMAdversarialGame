def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_dist(px, py):
        dmin = 10**9
        for rx, ry in resources:
            d = man(px, py, rx, ry)
            if d < dmin:
                dmin = d
        return dmin

    my_d0 = best_dist(sx, sy)
    opp_d0 = best_dist(ox, oy)

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # immediate collection priority
        collected = 1 if (nx, ny) in res_set else 0

        my_d1 = best_dist(nx, ny)

        # estimate opponent ability: they will likely move toward the same closest target
        # (use their current distance to our chosen cell's closest resource as a proxy)
        opp_d1 = 10**9
        # pick the resource that we would be closest to after moving
        # deterministically: the minimal man distance resource; tie-break lexicographically
        best_r = None
        best_rd = 10**9
        for rx, ry in resources:
            rd = man(nx, ny, rx, ry)
            if rd < best_rd or (rd == best_rd and (rx, ry) < best_r):
                best_rd = rd
                best_r = (rx, ry)
        rx, ry = best_r
        opp_d1 = man(ox, oy, rx, ry)

        # score: maximize collection, then maximize advantage in progress vs opponent
        # Convert to minimization-friendly components
        adv = (opp_d0 - opp_d1) - (my_d1 - my_d0)
        score = collected * 100000 + adv * 1000 - my_d1 - 0.1 * man(nx, ny, rx, ry) + 0.01 * (nx - sx) + 0.01 * (ny - sy)

        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]