def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Prefer resources we can reach no later than opponent; then maximize margin; then closeness.
    best = None
    for rx, ry in resources:
        self_d = md(sx, sy, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        margin = opp_d - self_d  # positive => we race faster
        # Denier-style: also consider that opponent might deny; favor bigger margin and smaller self distance.
        key = (-(self_d == 0),  # ensure we still can collect if on resource
               -abs(self_d),     # slight tie stability
               -margin,         # minimize negative margin => larger margin preferred
               self_d,          # then closer
               md(ox, oy, rx, ry))  # then further from opponent (reduces denial likelihood)
        # Re-map since key above uses negations; easier: compute deterministic scalar by tuple directly.
        # Use a direct tuple with clear ordering:
        key2 = (margin < 0, -margin, self_d, md(ox, oy, rx, ry), rx, ry)
        if best is None or key2 < best[0]:
            best = (key2, (rx, ry))

    _, (tx, ty) = best

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))

    if not valid:
        return [0, 0]

    # Choose move that most reduces distance to target; break ties by avoiding moves that help opponent race.
    cur_self_d = md(sx, sy, tx, ty)
    cur_opp_d = md(ox, oy, tx, ty)
    best_move = None
    best_score = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        self_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        reach_win = (self_d <= opp_d)
        # primary: make progress; secondary: keep race advantage; tertiary: deterministic tie on position
        score = (
            0 if reach_win else 1,
            self_d,                        # smaller is better
            -(cur_self_d - self_d),       # prefer larger improvement
            abs(nx - sx) + abs(ny - sy),  # prefer smaller move if equal
            nx, ny
        )
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]