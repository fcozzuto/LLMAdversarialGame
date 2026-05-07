def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Press toward opponent while avoiding obstacles
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                val = (man(nx, ny, ox, oy), 0, dx, dy)
                if best is None or val < best:
                    best = val
        return [0, 0] if best is None else [best[2], best[3]]

    # Greedy lookahead: pick move that yields best (self_distance_to_best_resource, -opponent_distance)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        chosen = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            if sd == 0:
                # Immediate pickup is best possible
                val = (-1, -man(ox, oy, rx, ry), rx, ry)
            else:
                val = (sd, -man(ox, oy, rx, ry), rx, ry)
            if chosen is None or val < chosen:
                chosen = val
        if chosen is None:
            continue
        # Prefer moves that can collect sooner; add tie-break toward resources that opponent is far from
        overall = (chosen[0], chosen[1], man(nx, ny, ox, oy), dx, dy)
        if best is None or overall < best:
            best = overall

    return [0, 0] if best is None else [best[3], best[4]]