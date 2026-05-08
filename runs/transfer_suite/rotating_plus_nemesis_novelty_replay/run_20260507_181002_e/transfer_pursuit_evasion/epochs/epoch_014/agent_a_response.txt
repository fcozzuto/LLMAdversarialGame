def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx != 0 or dy != 0:
                dirs.append((dx, dy))
    dirs.append((0, 0))

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    tx, ty = ox, oy
    chase_dx = 0 if tx == sx else (1 if tx > sx else -1)
    chase_dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Deterministic "orbit" when not improving: move perpendicular to the chase direction
    # using turn parity to avoid repeating a losing pursuit pattern.
    if observation.get("turn_index", 0) % 2 == 0:
        cand = [(chase_dx, chase_dy), (chase_dx, 0), (0, chase_dy)]
    else:
        # perpendicular for axial-aligned cases; for diagonal, rotate (dx,dy)->(dy,-dx)
        px, py = (chase_dy, -chase_dx)
        # if perpendicular is (0,0), fall back to direct chase candidates
        if px == 0 and py == 0:
            cand = [(chase_dx, chase_dy), (-chase_dx, chase_dy), (chase_dx, -chase_dy)]
        else:
            cand = [(px, py), (-px, py), (px, -py)]

    def score_move(mdx, mdy):
        nx, ny = sx + mdx, sy + mdy
        # prefer reducing distance to opponent
        d_before = (sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)
        d_after = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # small preference for mobility to avoid getting stuck behind obstacles
        mob = 0
        for ddx, ddy in dirs:
            if free(nx + ddx, ny + ddy):
                mob += 1
        # avoid moving into positions that are "tight" with few options
        # and slightly prefer moves that align with chase direction when possible
        align = 0
        if mdx == chase_dx:
            align += 1
        if mdy == chase_dy:
            align += 1
        # if orbiting, allow slight "stirring" by rewarding distance if chasing parity prefers it
        improving = d_after < d_before
        parity = observation.get("turn_index", 0) % 2
        orbit_bonus = 0.0
        if parity == 1 and not improving:
            orbit_bonus = 0.15 * (d_before - d_after)  # still favors changes, not necessarily monotonic
        return (d_before - d_after) * 10.0 + mob * 0.25 + align * 0.4 + orbit_bonus

    # pick best among legal, but ensure candidates are considered first deterministically
    cand_set = set(cand)
    best = None
    bestv = None
    for m in legal:
        mdx, mdy = m
        v = score_move(mdx, mdy)
        if bestv is None or v > bestv or (v == bestv and (mdx, mdy) in cand_set):
            bestv = v
            best = m

    # If best isn't in our primary candidate set, try forcing the best candidate that is legal.
    for m in cand:
        if m in legal:
            return [int(m[0]), int(m[1])]
    return [int(best[0]), int(best[1])]