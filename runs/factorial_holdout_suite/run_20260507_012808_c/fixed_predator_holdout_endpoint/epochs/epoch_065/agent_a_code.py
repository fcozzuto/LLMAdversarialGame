def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    # Filter valid resources (ignore those currently on obstacles, if any)
    valid = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                valid.append((x, y))
    if not valid:
        return [0, 0]

    # Prefer resources we can reach no slower than opponent; otherwise seek biggest "race" advantage.
    best = None
    best_s = -10**18
    for x, y in valid:
        sd = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)
        # Encourage guaranteed/near-guaranteed first pick and de-emphasize long races.
        race = od - sd  # positive means we are closer
        # Weight closer destinations more (fewer steps), and break ties against opponent closeness.
        s = (race * 100) + (20 - sd) * 3 - (0 if od == sd else (1 if od < sd else 0))
        if sd <= od:
            s += 200  # strong preference when we can arrive first or tie
        # Mild preference to avoid moving onto/near obstacles: penalize if target is adjacent to obstacles
        adj = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    adj += 1
        s -= adj * 2
        if s > best_s:
            best_s = s
            best = (x, y)

    tx, ty = best

    # Choose next move by minimizing distance to target while avoiding obstacles.
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_m = (0, 0)
    best_m_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        self_d = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(ox - nx) + abs(oy - ny)
        # Primary: get closer to target; Secondary: push away from opponent when race is close.
        m_s = -self_d * 10 + opp_d * (1 if abs(tx - ox) + abs(ty - oy) <= abs(tx - sx) + abs(ty - sy) + 1 else 0)
        if m_s > best_m_s:
            best_m_s = m_s
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]