def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    self_t = to_set("self_territory")
    opp_t = to_set("opponent_territory")
    un = to_set("unclaimed_cells")

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Target selection: prefer unclaimed cells that are "frontier" between us and opponent,
    # while not too far from us. Deterministic tie-breaking by coordinate.
    if un:
        best = None
        for x, y in un:
            ds = man(x, y, sx, sy)
            do = man(x, y, ox, oy)
            # Want closer to us, but also closer to opponent (frontier).
            score = ds - 0.65 * do + 0.001 * (x * 8 + y)
            if best is None or score < best[0]:
                best = (score, x, y)
        tx, ty = best[1], best[2]
    else:
        # If nothing unclaimed, push toward opponent.
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Scoring the immediate move. Flipping on entry => reward entering opponent cells.
        move_into_opp = (nx, ny) in opp_t
        move_into_un = (nx, ny) in un
        move_into_self = (nx, ny) in self_t

        # Base: reduce distance to target.
        dist = man(nx, ny, tx, ty)

        # Add shaping: prefer capturing (unclaimed or opponent territory).
        cap_bonus = 0.0
        if move_into_un:
            cap_bonus += 1.6
        if move_into_opp:
            cap_bonus += 3.2
        if move_into_self:
            cap_bonus -= 0.2  # less urgency staying inside our own territory

        # Small bias to keep motion directed toward opponent corner to sustain control.
        adv = -0.12 * man(nx, ny, ox, oy)

        score = dist - cap_bonus + adv + 0.0001 * (nx * 8 + ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]