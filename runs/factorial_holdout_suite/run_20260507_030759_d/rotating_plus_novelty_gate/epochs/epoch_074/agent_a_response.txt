def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    obstacles = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    resources = observation.get("resources", []) or []
    reslist = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]
    if (sx, sy) in set(reslist):
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal or not reslist:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    mypos = (sx, sy)
    opp = (ox, oy)

    # Newer policy: locally choose move that maximizes "secure-then-intercept":
    # - prefer actions that put us closer to the resource we can reach first,
    # - otherwise block by moving toward resources opponent is about to take,
    # - plus a small deterministic pressure to reduce distance to opponent.
    scored = []
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        newpos = (nx, ny)
        best_immediate = None
        for r in reslist:
            dm = md(newpos, r)
            do = md(opp, r)
            # If we can arrive no later than opponent, value is high.
            # If not, value still encourages blocking nearer-to-us positions.
            # Deterministic tie breaker by resource coords.
            win = (dm <= do)
            val = (0 if win else -1)  # allow win to dominate
            key = (val, dm - do, dm, r[0], r[1])
            if best_immediate is None or key < best_immediate:
                best_immediate = key
        # best_immediate: (winflag, dm-do, dm, rx, ry) with smaller better
        winflag, dmdiff, dm, rx, ry = best_immediate
        intercept = md(newpos, opp)
        # Higher is better => convert to minimizing key by negating components.
        score_key = (winflag, dmdiff, dm, intercept, dx + 2 * dy, rx, ry)
        scored.append((score_key, dx, dy))

    scored.sort()
    _, dx, dy = scored[0]
    return [int(dx), int(dy)]