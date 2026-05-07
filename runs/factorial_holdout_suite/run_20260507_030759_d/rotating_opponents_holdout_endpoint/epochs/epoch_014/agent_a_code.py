def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    if not (0 <= sx < w and 0 <= sy < h and 0 <= ox < w and 0 <= oy < h):
        return [0, 0]

    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                oset.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_sc = -10**18

    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int):
                if (x, y) not in oset:
                    res_list.append((x, y))

    if not res_list:
        # No resources: move to increase distance from opponent (deterministic fallback)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in oset:
                continue
            sc = md(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc = sc
                best_move = [dx, dy]
        return best_move

    # Choose step that maximizes advantage toward a resource we can likely reach sooner
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue
        sc = -md(nx, ny, ox, oy) * 0.01  # small bias: don't run into opponent
        for rx, ry in res_list:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            adv = do - ds  # positive if we are closer to this resource after the move
            sc2 = adv * 200 - ds  # prefer bigger advantage and nearer target
            if ds == 0:
                sc2 += 10**6
            sc += sc2
        # Normalize by number of resources considered to keep scale stable
        sc = sc / max(1, len(res_list))
        if sc > best_sc:
            best_sc = sc
            best_move = [dx, dy]

    return best_move