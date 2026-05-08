def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                unclaimed.append((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                opp_terr.add((x, y))

    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])
    self_terr = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                self_terr.add((x, y))

    dxdy = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    targets = unclaimed if unclaimed else list(opp_terr) if opp_terr else []
    tx, ty = None, None
    if targets:
        # Prefer unclaimed; else opponent territory; tie-break by distance to us then position
        if unclaimed:
            tx, ty = min(unclaimed, key=lambda c: (abs(c[0]-sx)+abs(c[1]-sy), c[0], c[1]))
        else:
            tx, ty = min(list(opp_terr), key=lambda c: (abs(c[0]-sx)+abs(c[1]-sy), c[0], c[1]))

    for dx, dy in dxdy:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        score = 0
        if (nx, ny) in opp_terr:
            score += 1200  # strong counterclaim
        elif (nx, ny) in unclaimed:
            score += 800   # claim
        elif (nx, ny) in self_terr:
            score += 30    # keep control

        # Frontier pressure: head toward nearest unclaimed (or opponent territory)
        if tx is not None:
            score += -10 * (abs(nx - tx) + abs(ny - ty))
        else:
            score += -4 * (abs(nx - ox) + abs(ny - oy))

        # Slightly avoid drifting away from center early; deterministic
        t = int(observation.get("turn_index") or 0)
        if t < 20:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score += -0.5 * ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]