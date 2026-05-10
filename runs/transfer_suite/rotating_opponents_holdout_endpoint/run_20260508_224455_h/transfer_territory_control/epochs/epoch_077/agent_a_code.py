def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obst = set()
    for c in observation.get("obstacles") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            obst.add((int(c[0]), int(c[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    oppT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    obstacles_present = bool(obst)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer capturing unclaimed, then flipping opponent territory.
    targets = []
    for c in unclaimed:
        targets.append((c[0], c[1], 2))
    for c in oppT:
        targets.append((c[0], c[1], 1))
    if not targets:
        return [0, 0]

    def score_target(x, y, kind):
        d = abs(x - sx) + abs(y - sy)
        # Small bias toward cells that are not yet controlled by us.
        bias = 0 if (x, y) in selfT else 0.2
        # Prefer moving toward targets that are not "behind" obstacles by penalizing blocked adjacent next-step (handled later).
        return d - kind * 1.5 - bias

    bestx, besty, bestk = None, None, None
    bestv = 10**9
    # Deterministic scan order
    targets.sort(key=lambda t: (t[0], t[1], t[2]))
    for x, y, kind in targets:
        v = score_target(x, y, kind)
        if v < bestv:
            bestv, bestx, besty, bestk = v, x, y, kind

    tx, ty = bestx, besty

    # Choose best move that reduces distance to the target (and avoids obstacles).
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if obstacles_present and (nx, ny) in obst:
            continue
        # Higher value is better.
        dist_now = abs(tx - sx) + abs(ty - sy)
        dist_next = abs(tx - nx) + abs(ty - ny)
        delta = dist_now - dist_next

        # Prefer stepping into unclaimed/opponent territory.
        gain = 0.0
        if (nx, ny) in unclaimed:
            gain += 3.0
        if (nx, ny) in oppT:
            gain += 1.5
        # Avoid stepping into our own territory only if it doesn't improve distance.
        if (nx, ny) in selfT and delta <= 0:
            gain -= 0.3

        # Mild center bias to prevent dithering.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = -(abs(nx - cx) + abs(ny - cy)) * 0.01

        val = delta * 2.0 + gain + center
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]