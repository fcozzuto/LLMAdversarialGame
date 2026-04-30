def choose_move(observation):
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # BFS distance on 8x8 avoiding obstacles
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def bfsdist(start, goal):
        if start == goal: return 0
        if goal in obstacles: return None
        q = [start]
        dist = {start: 0}
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d = dist[(x, y)] + 1
            for dx, dy in dirs[:-1]:  # exclude (0,0) for expansion
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in dist:
                    dist[(nx, ny)] = d
                    if (nx, ny) == goal: return d
                    q.append((nx, ny))
        return None
    def score_for_resource(r):
        sd = bfsdist((sx, sy), r)
        od = bfsdist((ox, oy), r)
        if sd is None and od is None: return -10**9
        if sd is None: return -10**8
        if od is None: return 10**6 - sd
        # Prefer resources where we are closer than opponent; add small tie-break for self closeness
        return (od - sd) * 100 - sd
    targets = resources if resources else []
    best_r = None
    best_s = -10**18
    for r in targets:
        s = score_for_resource(tuple(r))
        if s > best_s:
            best_s, best_r = s, tuple(r)
    if best_r is None:
        # Fallback: move to keep distance while not colliding with obstacles
        best_move = [0, 0]
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): continue
            # maximize distance from opponent
            val = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            if val > best_val:
                best_val, best_move = val, [dx, dy]
        return best_move
    # Choose move that minimizes distance to target, then maximizes advantage
    cur_sd = bfsdist((sx, sy), best_r)
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): continue
        nsd = bfsdist((nx, ny), best_r)
        nod = bfsdist((ox, oy), best_r)
        if nsd is None: 
            continue
        # Lower nsd is better; higher opponent distance advantage is better
        val = -nsd * 1000 + (nod - nsd) * 10
        # Small tie-break: prefer moves that reduce current self distance
        if cur_sd is not None:
            val += (cur_sd - nsd)
        if val > best_val:
            best_val, best_move = val, [dx, dy]
    return best_move