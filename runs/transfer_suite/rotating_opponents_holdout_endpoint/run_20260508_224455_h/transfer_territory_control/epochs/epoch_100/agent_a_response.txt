def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    path = observation.get("self_path") or []
    recent = set()
    for p in path[-8:]:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            recent.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs8 = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]

    def adj_count_set(x, y, s):
        c = 0
        for dx, dy in dirs8:
            if (x+dx, y+dy) in s:
                c += 1
        return c

    best = (0, 0, -10**18)  # dx,dy,val
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) in opp_terr:
            val += 18  # flip to us on entry (flipping enabled)
        elif (nx, ny) in unclaimed:
            val += 12  # immediate claim
        elif (nx, ny) in self_terr:
            val += 4
        else:
            val += 1

        # Expand from our borders
        val += 2 * adj_count_set(nx, ny, self_terr)

        # Incentivize pushing into opponent area by being adjacent to it
        val += 3 * adj_count_set(nx, ny, opp_terr)

        # Discourage oscillation
        if (nx, ny) in recent and (dx, dy) != (0, 0):
            val -= 20

        # Mild center-bias to avoid getting stuck on corners
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist = abs(nx - cx) + abs(ny - cy)
        val -= 0.2 * dist

        if val > best[2] or (val == best[2] and (dx, dy) < (best[0], best[1])):
            best = (dx, dy, val)

    return [int(best[0]), int(best[1])]