def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    targets = []
    for r in resources:
        x = y = None
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        elif isinstance(r, dict):
            pos = r.get("position", r.get("pos", None))
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                x, y = int(pos[0]), int(pos[1])
        if x is not None and y is not None and inb(x, y) and (x, y) not in obs:
            targets.append((x, y))
    if not targets:
        return [0, 0]

    best = None
    for tx, ty in targets:
        ds = abs(tx - sx) + abs(ty - sy)
        do = abs(tx - ox) + abs(ty - oy)
        if best is None or (ds - 0.7 * do) < best[0]:
            best = (ds - 0.7 * do, tx, ty)
    _, tx, ty = best

    best_move = (0, 0, 10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ns = abs(tx - nx) + abs(ty - ny)
        no = abs(tx - ox) + abs(ty - oy)
        block = 0
        if (nx, ny) == (ox, oy):
            block += 1000
        # Prefer getting closer; if opponent is closer, add stronger contest pressure.
        metric = ns - 1.1 * no + block
        # Mild anti-stall: prefer moves that change position unless trapped.
        if (dx, dy) != (0, 0):
            metric -= 0.05
        if metric < best_move[2]:
            best_move = (dx, dy, metric)

    if best_move[2] >= 10**9:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]