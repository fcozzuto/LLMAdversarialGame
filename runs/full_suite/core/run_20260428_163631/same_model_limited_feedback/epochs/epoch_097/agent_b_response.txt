def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def step_to(tx, ty, cx, cy):
        dx = 0 if tx == cx else (1 if tx > cx else -1)
        dy = 0 if ty == cy else (1 if ty > cy else -1)
        return dx, dy
    def manh(a,b,c,d): return abs(a-c) + abs(b-d)
    # Target: resource where we are relatively closest vs opponent; if tie, prefer farthest from opponent (disruptive).
    if resources:
        best = None
        for rx, ry in resources:
            myd = max(0, manh(sx,sy,rx,ry))
            opd = max(0, manh(ox,oy,rx,ry))
            score = (opd - myd) * 10 - myd
            # If I'm already on it (rare due to turn order), highest priority.
            if rx == sx and ry == sy: score += 100000
            # Disruption: prefer resources where opponent is not close.
            score += (w + h - opd) * 0.1
            if best is None or score > best[0]: best = (score, rx, ry)
        _, tx, ty = best
        # If obstacle blocks direct progress, bias to alternate step that still improves my distance.
        desired = step_to(tx, ty, sx, sy)
        candidates = []
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Primary: progress toward target.
            myd0 = manh(sx, sy, tx, ty)
            myd1 = manh(nx, ny, tx, ty)
            # Secondary: avoid giving opponent an immediate capture advantage (new change).
            # If opponent is closer to the same target after my move, penalize.
            opd_after = manh(ox, oy, tx, ty)
            # Opponent movement is unknown; use current proximity as a proxy.
            oppd = manh(ox, oy, tx, ty)
            val = (myd0 - myd1) * 100 - myd1
            val += (oppd - myd1) * 0.5
            # Extra: if I can land on a resource, strongly prefer it.
            if (nx, ny) in set(tuple(p) for p in resources):
                val += 10000
            candidates.append((val, dx, dy, abs(nx-tx)+abs(ny-ty)))
        if candidates:
            candidates.sort(key=lambda t: (-t[0], t[3], t[1], t[2]))
            return [int(candidates[0][1]), int(candidates[0][2])]
        return [int(desired[0]), int(desired[1])]
    # No resources left: new defensive strategy—move to maximize distance from opponent while avoiding obstacles.
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = (abs(nx-ox) + abs(ny-oy))
        # Also nudge toward center to avoid corner trapping.
        center_bias = -(abs((w-1)/2 - nx) + abs((h-1)/2 - ny))
        val = d * 10 + center_bias
        if best is None or val > best[0]:
            best = (val, dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]