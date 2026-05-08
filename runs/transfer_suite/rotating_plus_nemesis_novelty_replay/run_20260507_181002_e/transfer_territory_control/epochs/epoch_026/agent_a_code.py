def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    if not unclaimed:
        resources = toset(observation.get("resources"))
        unclaimed = resources

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    oppd = max(abs(ox - sx), abs(oy - sy))
    best = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        is_self = (nx, ny) in selfT
        is_opp = (nx, ny) in oppT
        is_uncl = (nx, ny) in unclaimed
        dist_to_center = abs(nx - cx) + abs(ny - cy)

        # Threat control: if opponent is very close, avoid stepping into neutral/unclaimed if possible.
        cheb_to_opp = max(abs(nx - ox), abs(ny - oy))
        near_opp_pen = 0
        if cheb_to_opp <= 1 and not is_self:
            near_opp_pen = 2.5
        if cheb_to_opp == 0:
            near_opp_pen = 5.0

        # Greedy territory expansion with mild center bias and opponent-interaction bonus.
        score = 0.0
        if is_uncl: score += 2.2
        if is_opp: score += 1.8  # can flip on entry
        if is_self: score += 0.4
        score += 0.15 * (oppd - max(abs(ox - nx), abs(oy - ny)))  # prefer moving away when safe
        score += -0.03 * dist_to_center
        score -= near_opp_pen

        # If unclaimed exists, prefer moving closer to nearest unclaimed cell.
        if unclaimed:
            mind = 10**9
            for tx, ty in unclaimed:
                d = abs(tx - nx) + abs(ty - ny)
                if d < mind:
                    mind = d
            score += -0.08 * mind

        if score > best:
            best = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]