def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    resources = set((int(p[0]), int(p[1])) for p in (observation.get("resources") or []))

    def manh(x, y):
        return abs(x - ox) + abs(y - oy)

    def eval_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in resources:
            base = 80
        else:
            base = 0
        if (x, y) in opp_terr:
            # flipping on entry
            base += 260 - 0.3 * manh(x, y)
        elif (x, y) in unclaimed:
            base += 140 - 0.15 * manh(x, y)
        elif (x, y) in self_terr:
            base += 30 - 0.05 * manh(x, y)
        else:
            base += 60 - 0.1 * manh(x, y)  # usually "neutral/untracked"
        # prefer moving closer to opponent early in the game
        t = int(observation.get("turn_index", 0))
        progress = min(1.0, max(0.0, t / 64.0))
        base += (progress * 10.0) * (manh(sx, sy) - manh(x, y))
        return base

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        sc = eval_cell(nx, ny)
        if best is None or sc > best_score or (sc == best_score and (dx, dy) < best):
            best_score = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]