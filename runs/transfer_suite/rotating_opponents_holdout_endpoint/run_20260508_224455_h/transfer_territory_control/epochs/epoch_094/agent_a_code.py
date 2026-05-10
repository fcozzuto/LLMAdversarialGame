def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    recent = set()
    path = observation.get("self_path") or []
    for p in path[-10:]:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            recent.add((int(p[0]), int(p[1])))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    def score_cell(x, y):
        p = (x, y)
        if p in obstacles: return -10**9
        if not inb(x, y): return -10**9
        s = 0
        if p in unclaimed: s += 50
        if p in opp_terr: s += 120  # flipping on entry
        if p in self_terr: s += 10
        # Prefer expanding near our current territory
        adj_ours = 0
        for dx, dy in dirs:
            nx, ny = x+dx, y+dy
            if inb(nx, ny) and (nx, ny) in self_terr:
                adj_ours += 1
        s += adj_ours * 8
        # Avoid getting stuck bouncing
        if p in recent: s -= 20
        # Prefer closing to nearby unclaimed frontier
        if unclaimed:
            best_u = 10**9
            for dx, dy in dirs:
                nx, ny = x+dx, y+dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    best_u = 0
                    break
            if best_u != 0:
                # cheap look: only check small neighborhood
                for xx in range(max(0, x-2), min(w, x+3)):
                    for yy in range(max(0, y-2), min(h, y+3)):
                        if (xx, yy) in unclaimed:
                            d = abs(xx-x) + abs(yy-y)
                            if d < best_u: best_u = d
            if best_u != 10**9: s += max(0, 10 - best_u) * 3
        # Pull toward opponent territory center-ish (deterministic, cheap)
        if opp_terr:
            # compute a deterministic pseudo-centroid by averaging with truncation
            ox = sum(xx for xx, yy in list(opp_terr)[:20]) // max(1, min(20, len(opp_terr)))
            oy = sum(yy for xx, yy in list(opp_terr)[:20]) // max(1, min(20, len(opp_terr)))
            s -= man((x, y), (ox, oy)) * 0.2
        return s

    # Candidate moves: choose best next cell by heuristic
    best = None
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx+dx, sy+dy
        s = score_cell(nx, ny)
        # slight tie-break toward staying in bounds center-ish
        if inb(nx, ny) and (nx, ny) not in obstacles:
            tie = (abs(nx - (w-1)/2) + abs(ny - (h-1)/2)) * 1e-6
        else:
            tie = 0
        s2 = s - tie
        if s2 > best_s or (s2 == best_s and (nx, ny) < best):
            best_s = s2
            best = (nx, ny)

    if best is None:
        return [0, 0]
    dx = best[0] - sx
    dy = best[1] - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]