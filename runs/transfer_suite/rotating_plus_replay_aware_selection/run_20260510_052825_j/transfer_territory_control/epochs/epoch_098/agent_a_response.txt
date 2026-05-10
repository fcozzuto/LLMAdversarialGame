def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (-1, -1))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) == 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) == 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) == 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) == 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Candidate targets: prefer unclaimed adjacent to our territory to secure fronts.
    frontier = set()
    if selfT:
        for x, y in selfT:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    frontier.add((nx, ny))
    targets = list(frontier) if frontier else list(unclaimed)
    if not targets:
        # If no unclaimed, drift toward opponent-owned cells (flipping enabled) if allowed.
        targets = list(oppT) if oppT else [(sx, sy)]

    def step_eval(nx, ny):
        if (nx, ny) in obstacles or not inb(nx, ny):
            return -10**9
        # Base: claim value, then proximity to best targets, then avoid giving opponent easy capture.
        best_t = 10**9
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < best_t:
                best_t = d
        # If moving into opponent territory, that's usually good (flipping on entry).
        flip_bonus = 5 if (nx, ny) in oppT else 0
        # Encourage moving toward tiles that are near unclaimed relative to opponent.
        opp_adv = 0
        if inb(ox, oy):
            best_o = 10**9
            for tx, ty in targets:
                d = abs(tx - ox) + abs(ty - oy)
                if d < best_o:
                    best_o = d
            opp_adv = best_o - best_t  # positive if we are closer than opponent to some target
        center_tie = - (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) * 0.01
        # Small deterministic tie-break: keep ordering by dx,dy later.
        return (flip_bonus * 100.0) + (-best_t * 10.0) + (opp_adv * 2.0) + center_tie

    best_score = -10**18
    best_move = [0, 0]
    # Deterministic tie-break order.
    ordered = sorted(dirs, key=lambda t: (t[0], t[1]))
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        sc = step_eval(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]