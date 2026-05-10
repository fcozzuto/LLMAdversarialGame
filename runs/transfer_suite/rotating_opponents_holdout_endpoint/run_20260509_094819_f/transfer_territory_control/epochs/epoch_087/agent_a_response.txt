def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    obs_cells = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_cells.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs_cells:
                targets.append((x, y))

    # Prefer capturing nearby unclaimed; otherwise expand toward center.
    if targets:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        targets.sort(key=lambda t: (abs(t[0] - cx) + abs(t[1] - cy), abs(t[0] - sx) + abs(t[1] - sy)))
        tx, ty = targets[0]
    else:
        tx, ty = (w // 2), (h // 2)

    opp = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(opp[0]), int(opp[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))
    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        if (nx, ny) in obs_cells:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Heuristic: go toward target, avoid staying on already controlled cells too long,
        # and avoid stepping into opponent territory when alternatives exist (but allow if best).
        dist = abs(nx - tx) + abs(ny - ty)
        gain = 0
        if (nx, ny) not in self_terr:
            gain += 3
        if (nx, ny) in opp_terr:
            gain -= 1.5
        # Slightly prefer moves that don't allow opponent to be immediately adjacent after move.
        adj_opp = max(abs(nx - ox), abs(ny - oy))
        opp_pen = 0.4 * (1.0 / (1.0 + adj_opp))
        score = (-dist) + gain - opp_pen

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]