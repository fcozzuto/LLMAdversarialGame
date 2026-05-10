def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    res = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Candidate-target: prioritize resources that are "sweep-row friendly" against a row-sweeping opponent:
    # prefer those on opponent's current row/column; otherwise closest race.
    def target_priority(cell):
        dso = man((ox, oy), cell)
        ds = man((sx, sy), cell)
        same_row = 1 if cell[1] == oy else 0
        same_col = 1 if cell[0] == ox else 0
        # higher is better; incorporate deny value (opponent_time - self_time)
        deny = (dso - ds)
        return (same_row + same_col, deny, -ds, cell[0], cell[1])

    target_list = sorted(res, key=target_priority, reverse=True)[:6]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # If opponent is close to a target on next steps, bias against it unless we can win the race.
        s_pos = (nx, ny)
        score = 0
        for t in target_list:
            ds = man(s_pos, t)
            od = man((ox, oy), t)
            # win race gets big boost; losing gets penalty scaled by how badly
            win = ds <= od
            deny = od - ds
            sweep_bonus = 2 if (t[1] == oy or t[0] == ox) else 0
            score += (10 if win else -6) + sweep_bonus + (deny // 2)
        # small stability: avoid moving away from the top target
        top = target_list[0]
        score -= man((nx, ny), top) - man((sx, sy), top)
        # deterministic tie-break: prefer moves that reduce distance to top target, then lexicographic
        tie = (man((nx, ny), top), dx, dy)
        cand = (score, -tie[0], -tie[1], -tie[2])
        if best_score is None or cand > best_score:
            best_score = cand
            best_move = (dx, dy)

    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]