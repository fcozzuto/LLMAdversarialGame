def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = observation.get("unclaimed_cells", []) or []
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr_list = observation.get("opponent_territory", []) or []
    opp_terr = set(map(tuple, opp_terr_list))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    target = None
    if unclaimed:
        best = None
        for tx, ty in unclaimed:
            if not inb(tx, ty) or (tx, ty) in obstacles: 
                continue
            ds = man(sx, sy, tx, ty)
            do = man(ox, oy, tx, ty)
            # Prefer cells nearer to us, also towards center, and away from opponent.
            key = (ds, abs(tx - cx) + abs(ty - cy), -do)
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        if best is not None:
            target = best[1]
    if target is None and opp_terr_list:
        # If no unclaimed (or blocked), pressure opponent territory.
        best = None
        for tx, ty in opp_terr_list:
            if not inb(tx, ty) or (tx, ty) in obstacles:
                continue
            ds = man(sx, sy, tx, ty)
            key = (ds, -man(ox, oy, tx, ty))
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        if best is not None:
            target = best[1]
    if target is None:
        return [0, 0]

    tx, ty = target
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_score = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        immediate = 0
        if (nx, ny) in opp_terr:
            immediate += 20  # likely flip
        elif (nx, ny) in unclaimed:
            immediate += 8
        elif (nx, ny) in self_terr:
            immediate += 1
        # Move toward target, but keep distance from opponent.
        dist_to_t = man(nx, ny, tx, ty)
        dist_opp = man(nx, ny, ox, oy)
        center_bias = -(abs(nx - cx) + abs(ny - cy)) / 8.0
        score = immediate - 2.0 * dist_to_t + 0.5 * dist_opp + center_bias
        # Slight preference for not changing direction if tied by biasing toward target.
        if best_score is None or score > best_score + 1e-9:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]