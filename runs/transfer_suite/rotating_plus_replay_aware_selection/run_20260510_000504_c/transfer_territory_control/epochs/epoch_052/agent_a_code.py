def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    unclaimed_set = set(map(tuple, unclaimed))
    if not unclaimed and resources:
        unclaimed = resources

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in opp_terr:
            return 120 - (abs(x - sx) + abs(y - sy))  # direct flip attempt
        if (x, y) in unclaimed_set or (x, y) in resources:
            near_opp = 0
            near_self = 0
            for nx, ny in neigh(x, y):
                if (nx, ny) in opp_terr:
                    near_opp += 1
                if (nx, ny) in self_terr:
                    near_self += 1
            # Edge pressure: prioritize being near opponent, then expand our region.
            return 80 * near_opp + 35 * near_self - (abs(x - sx) + abs(y - sy)) - (x + y) * 0.01
        # If everything is claimed, stay focused near opponent territory boundary
        # and avoid our own dead-ends by favoring cells closer to opponent.
        return 10 - (abs(x - opp_pos[0]) + abs(y - opp_pos[1]))

    # Build candidate target list deterministically
    candidates = []
    for x, y in unclaimed_set:
        s = score_cell(x, y)
        if s > 0:
            candidates.append((s, y, x))
    if resources:
        for rx, ry in resources:
            if (rx, ry) not in unclaimed_set:
                candidates.append((score_cell(rx, ry), ry, rx))
    if not candidates and opp_terr:
        for x, y in sorted(opp_terr):
            candidates.append((score_cell(x, y), y, x))
    if not candidates:
        candidates = [(score_cell(w - 1, h - 1), h - 1, w - 1)]

    _, ty, tx = max(candidates, key=lambda t: (t[0], -t[2], -t[1]))
    dx_list = (-1, 0, 1)
    best_move = [0, 0]
    best_val = -10**18

    for dx in dx_list:
        for dy in dx_list:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            v = - (abs(nx - tx) + abs(ny - ty))
            # Prefer stepping into opponent/unclaimed/frontier to capture.
            v += 70 if (nx, ny) in opp_terr else 0
            v += 35 if (nx, ny) in unclaimed_set else 0
            v += sum(1 for ax, ay in neigh(nx, ny) if (ax, ay) in opp_terr) * 12
            v += sum(1 for ax, ay in neigh(nx, ny) if (ax, ay) in self_terr) * 6
            # Tie-break deterministically: smaller dy then smaller dx, then stay if equal
            if v > best_val or (v == best_val and (dy, dx, nx, ny) < (best_move[1], best_move[0], sx + best_move[0], sy + best_move[1])):
                best_val = v
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]