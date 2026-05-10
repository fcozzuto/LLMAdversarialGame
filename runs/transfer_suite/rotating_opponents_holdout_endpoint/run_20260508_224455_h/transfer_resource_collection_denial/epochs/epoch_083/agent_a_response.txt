def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources") or [])]
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def steps(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # 8-dir distance

    if not resources:
        return [0, 0]

    turns_remaining = int(observation.get("turns_remaining", 0))

    best = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        ds = steps(sx, sy, rx, ry)
        do = steps(ox, oy, rx, ry)
        earlier = 1 if ds <= do else 0
        # Sweep-row opponent tendency: avoid resources on/near opponent's current row.
        row_pen = 0
        if ry == oy:
            row_pen = 3
        elif abs(ry - oy) == 1:
            row_pen = 1
        # Time pressure: closer gets more important.
        time_boost = max(0, (turns_remaining // 8) - ds)
        cand = (earlier, (do - ds) - row_pen + time_boost, -ds, rx, ry)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]

    tx, ty = best[3], best[4]
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If chosen neighbor hits obstacle, try deterministic alternatives.
    if (sx + dx, sy + dy) in obstacles:
        opts = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best2 = None
        for mx, my in opts:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = steps(nx, ny, tx, ty)
            cand2 = (-d, mx, my)
            if best2 is None or cand2 > best2:
                best2 = cand2
        return [int(best2[1]), int(best2[2])] if best2 else [0, 0]

    return [int(dx), int(dy)]