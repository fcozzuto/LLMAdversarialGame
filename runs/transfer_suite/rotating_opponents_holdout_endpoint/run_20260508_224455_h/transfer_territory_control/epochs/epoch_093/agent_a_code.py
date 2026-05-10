def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    path = observation.get("self_path") or []
    recent = set()
    for p in path[-8:]:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            recent.add((int(p[0]), int(p[1])))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Pick a target deterministically: nearest among (unclaimed, then opponent)
    candidates = []
    for c in unclaimed:
        candidates.append((man((sx, sy), c), c))
    if candidates:
        candidates.sort(key=lambda t: (t[0], t[1][0], t[1][1]))
        target = candidates[0][1]
    else:
        opp_list = [(man((sx, sy), c), c) for c in opp_set]
        opp_list.sort(key=lambda t: (t[0], t[1][0], t[1][1]))
        target = opp_list[0][1] if opp_list else (sx, sy)

    best_move = (0, 0)
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0.0
        cell = (nx, ny)

        # Immediate value for capturing/flipping
        if cell in opp_set:
            sc += 8.0
        elif cell in unclaimed:
            sc += 4.0
        elif cell in self_set:
            sc += 1.0
        else:
            sc += 0.2

        # Encourage moving toward target
        if target != (sx, sy):
            d0 = man((sx, sy), target)
            d1 = man((nx, ny), target)
            sc += (d0 - d1) * 1.2

        # Border pressure: if moving adjacent to opponent territory, increase likelihood to expand
        adj_opp = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in opp_set:
                    adj_opp += 1
        sc += adj_opp * 0.9

        # Avoid loops/revisits
        if cell in recent:
            sc -= 2.0

        # Soft penalty if both coordinates unchanged (stay)
        if dx == 0 and dy == 0:
            sc -= 0.3

        # Deterministic tie-break by preference order
        if sc > best_sc or (sc == best_sc and (dx, dy) < best_move):
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]