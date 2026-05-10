def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    path = observation.get("self_path") or []
    recent = set()
    for p in path[-8:]:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            recent.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cell_score(x, y):
        p = (x, y)
        if not inb(x, y) or p in obstacles: return -10**9
        s = 0
        if p in unclaimed: s += 80
        if p in opp_terr: s += 160  # flipping on entry
        if p in self_terr: s += 8
        # Frontier: value being adjacent to our territory (easy expansion) and to unclaimed/opp
        adj = 0; adj_u = 0; adj_o = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = x+dx, y+dy
            if inb(nx, ny):
                q = (nx, ny)
                if q in self_terr: adj += 1
                if q in unclaimed: adj_u += 1
                if q in opp_terr: adj_o += 1
        s += 6 * adj + 5 * adj_u + 4 * adj_o
        # Avoid traps/cycles
        if p in recent: s -= 35
        # Mild pull toward center late game
        tr = int(observation.get("turn_index", 0))
        wmid = (w - 1) / 2.0; hmid = (h - 1) / 2.0
        dist_center = abs(x - wmid) + abs(y - hmid)
        s -= int(0.3 * dist_center * (0.6 if tr > 40 else 0.3))
        return s

    # If we have a direct capture move adjacent to opponent territory, prioritize it deterministically.
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_terr:
            candidates.append((dx, dy, 10**9))
    if candidates:
        candidates.sort(key=lambda t: (-t[2], abs(t[0]) + abs(t[1]), t[0], t[1]))
        return [int(candidates[0][0]), int(candidates[0][1])]

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = cell_score(nx, ny)
        if sc > best_score or (sc == best_score and (best is None or (abs(dx)+abs(dy), dx, dy) < (abs(best[0])+abs(best[1]), best[0], best[1]))):
            best_score = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]