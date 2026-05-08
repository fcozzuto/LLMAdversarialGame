def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    self_t = set()
    for p in observation.get("self_territory") or []:
        try:
            self_t.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        try:
            opp_t.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))
        except Exception:
            pass

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_key = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        base = 0
        if cell in opp_t:
            base = 30
        elif cell in unclaimed:
            base = 18
        elif cell in self_t:
            base = 6
        else:
            base = 2

        # Prefer cells that are nearer to us than to opponent (territory counter-claim pressure)
        ds = abs(nx - sx) + abs(ny - sy)
        do = abs(nx - ox) + abs(ny - oy)
        rel = (do - ds)

        # Nudge toward cutting: if opponent nearby, prioritize their territory or nearby frontier
        opp_dist = abs(nx - ox) + abs(ny - oy)
        near_bonus = 8 if opp_dist <= 2 else 0

        # Tie-break deterministically: prefer smaller dx/dy lexicographic order after score
        score = base + rel + near_bonus - 0.001 * (ds + 0.5 * opp_dist)

        key = (-(score), dx, dy, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]