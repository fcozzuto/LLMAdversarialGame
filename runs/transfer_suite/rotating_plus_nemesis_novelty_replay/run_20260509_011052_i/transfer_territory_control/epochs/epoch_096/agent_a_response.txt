def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_t = set()
    for p in observation.get("self_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_t.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    res = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))

    targets = res if res else unclaimed
    if not targets:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # pick an "interception" target: near opponent territory if possible
    if opp_t:
        bestT = None
        bestD = 10**9
        for t in targets:
            if t in obs: 
                continue
            # distance to nearest opponent cell (cheaper than full search)
            d = min(abs(t[0]-px) + abs(t[1]-py) for px, py in (list(opp_t)[:30]))
            val = d + (abs(t[0]-sx) + abs(t[1]-sy)) * 0.35
            if val < bestD:
                bestD, bestT = val, t
        target = bestT if bestT is not None else targets[0]
    else:
        target = min(targets, key=lambda t: abs(t[0]-sx) + abs(t[1]-sy))

    best_move = [0, 0]
    best_score = -10**18
    tx, ty = target

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # immediate value: capture opponent, advance to target, avoid walking into opponent bulk
        score = 0.0
        if (nx, ny) in opp_t:
            score += 120.0
        if (nx, ny) in self_t:
            score += -2.0
        if (nx, ny) not in self_t and (nx, ny) not in opp_t:
            # likely unclaimed; prefer moving toward target
            score += 18.0

        # progress toward chosen target
        dist_now = abs(sx - tx) + abs(sy - ty)
        dist_next = abs(nx - tx) + abs(ny - ty)
        score += (dist_now - dist_next) * 3.5

        # keep a bit of spacing from opponent territory unless capturing it
        if (nx, ny) not in opp_t and opp_t:
            nearest = min(abs(nx-px) + abs(ny-py) for px, py in (list(opp_t)[:30]))
            score += max(0, 8 - nearest) * 1.5 * (-1 if nearest <= 2 else 1)

        # deterministic tie-break: prefer diagonal, then right, then down, then up
        tie = (dx, dy)
        score += (0.01 * (dx * 2 + dy))

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move