def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
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

    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        a -= c
        b -= d
        if a < 0: a = -a
        if b < 0: b = -b
        return a + b

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                if (nx, ny) in obstacles:
                    continue
            moves.append((dx, dy, nx, ny))

    # Prefer resources we are strictly closer to than opponent; else go for best overall.
    best_move = None
    best_val = -10**18
    best_tie = 10**18
    for dx, dy, nx, ny in moves:
        self_best = 10**18
        opp_best = 10**18
        val_best = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Advantage: positive means we can reach first (tie-break via smaller sd).
            val = od - sd
            # Small deterministic preference for nearer resources.
            val -= 0.01 * sd
            if val > val_best:
                val_best = val
                self_best = sd
                opp_best = od
            elif val == val_best:
                if sd < self_best:
                    self_best = sd
                    opp_best = od
        # Global move scoring: maximize advantage, then minimize our distance to the selected target.
        # If no positive advantage exists, still minimize our distance.
        score = val_best
        tie = self_best
        if (score > best_val) or (score == best_val and tie < best_tie):
            best_val = score
            best_tie = tie
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]