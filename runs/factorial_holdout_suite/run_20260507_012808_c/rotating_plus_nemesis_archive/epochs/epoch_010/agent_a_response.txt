def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        # Contested target: maximize our relative advantage to the most beatable resource.
        max_adv = -10**9
        min_self_to_any = 10**9
        tie = 0
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - self_d
            if adv > max_adv:
                max_adv = adv
            if self_d < min_self_to_any:
                min_self_to_any = self_d
            # deterministic tie-break: prefer parity alignment to reduce cycles
            tie = (tie + ((rx + ry) & 1)) & 1

        # If we can't get ahead (max_adv <= 0), prioritize fastest progress.
        # Also slightly prefer moves closer to the best resource set.
        key = (max_adv, -min_self_to_any, -(((nx + ny) & 1) ^ tie), -abs(ox - nx) - abs(oy - ny))
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return best_move