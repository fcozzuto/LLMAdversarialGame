def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    targets = list(unclaimed)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    if targets:
        targets.sort(key=lambda t: (dist2(t[0], t[1], cx, cy), abs(t[0] - ox) + abs(t[1] - oy)))
        target = targets[0]
    else:
        # fall back: head toward opponent's nearest non-obstacle cell around center
        all_cells = []
        for x in range(w):
            for y in range(h):
                if (x, y) not in obstacles:
                    all_cells.append((x, y))
        all_cells.sort(key=lambda t: (dist2(t[0], t[1], cx, cy), abs(t[0] - sx) + abs(t[1] - sy)))
        target = all_cells[0] if all_cells else (sx, sy)

    un = unclaimed
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        gain = 0
        if (nx, ny) in self_terr:
            gain += 2.0
        elif (nx, ny) in opp_terr:
            # entering opponent territory flips control; prioritize captures
            gain += 8.0
        elif (nx, ny) in un:
            gain += 6.0
        else:
            gain += 1.0

        # prefer cells that advance toward center-target and away from opponent's position
        toward = dist2(nx, ny, target[0], target[1])
        step_toward = -toward
        center_adv = -dist2(nx, ny, cx, cy) * 0.05
        away_from_opp = dist2(nx, ny, ox, oy) * 0.01
        score = gain + step_toward + center_adv + away_from_opp

        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]