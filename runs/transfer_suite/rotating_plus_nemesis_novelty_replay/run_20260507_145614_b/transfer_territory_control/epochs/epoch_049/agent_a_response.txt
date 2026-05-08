def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))

    self_terr = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    opp_pos = observation["opponent_position"]
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Find "frontier" direction: nearest unclaimed to opponent; then our move should approach it.
    target = None
    if unclaimed:
        best = None
        for (x, y) in unclaimed:
            # Prefer cells near opponent side, but not too far from us.
            k = (dist(ox, oy, x, y), dist(sx, sy, x, y), x, y)
            if best is None or k < best:
                best = k
                target = (x, y)

    def cell_type_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if (nx, ny) in unclaimed:
            return 1000
        if (nx, ny) in opp_terr:
            return 650
        if (nx, ny) in self_terr:
            return 60
        return 10

    best_move = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        base = cell_type_score(nx, ny)

        # If we have a target, approach it; otherwise, advance toward opponent position.
        if target is not None:
            tx, ty = target
            d_t = dist(nx, ny, tx, ty)
            d_o = dist(nx, ny, ox, oy)
            # Greedy blend: want closer to target, but also keep pressure toward opponent.
            key = (-base, d_t, d_o, abs(dx), abs(dy), nx, ny)
        else:
            d_o = dist(nx, ny, ox, oy)
            key = (-base, d_o, nx, ny, abs(dx), abs(dy))

        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move