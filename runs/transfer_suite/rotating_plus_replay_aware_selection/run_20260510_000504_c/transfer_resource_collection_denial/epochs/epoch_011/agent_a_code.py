def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def parse_resources():
        out = []
        for r in observation.get("resources", []) or []:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                out.append((int(r[0]), int(r[1])))
            elif isinstance(r, dict):
                pos = r.get("position", None)
                if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                    out.append((int(pos[0]), int(pos[1])))
                elif "x" in r and "y" in r:
                    out.append((int(r["x"]), int(r["y"])))
        return out

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for p in parse_resources():
        if p not in obstacles:
            res.append(p)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not res:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    # Prefer resources where we are closer than opponent; also lightly avoid stepping adjacent to obstacles.
    # Keep only a few best candidates to stay concise.
    candidates = []
    for rx, ry in res:
        md = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        candidates.append((md - od, md, rx, ry))
    candidates.sort()
    candidates = candidates[:4]

    def step_score(nx, ny):
        if (nx, ny) in obstacles or not inb(nx, ny):
            return -10**9
        s = 0.0
        for adv, md, rx, ry in candidates:
            myd = abs(rx - nx) + abs(ry - ny)
            opd = abs(rx - ox) + abs(ry - oy)
            # Big reward if we can reach first; secondary reward for reducing distance.
            s += 2.5 * (opd - myd) - 0.15 * myd
            if myd == 0:
                s += 50.0
        # Micro-avoid: prefer not to get boxed near obstacles.
        adj_obs = 0
        for ddx, ddy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            x2, y2 = nx + ddx, ny + ddy
            if inb(x2, y2) and (x2, y2) in obstacles:
                adj_obs += 1
        s -= 0.8 * adj_obs
        # Tie-break: nudge toward opponent only if it doesn't hurt resource race (small weight).
        s -= 0.02 * (abs(ox - nx) + abs(oy - ny))
        return s

    best = (0, 0)
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = step_score(nx, ny)
        if sc > best_s:
            best_s = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]