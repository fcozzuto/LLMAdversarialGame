def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    unclaimed = []
    for c in observation.get("unclaimed_cells") or []:
        try:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))
        except Exception:
            pass

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not unclaimed:
        # Fallback: move toward center-adjacent but deterministic and obstacle-safe
        cx, cy = (w - 1) // 2, (h - 1) // 2
        target = (cx, cy)
    else:
        # Target: unclaimed that we can reach better than opponent (tie-break by coordinates)
        best = None
        best_key = None
        for x, y in unclaimed:
            d1 = abs(x - sx) + abs(y - sy)
            d2 = abs(x - ox) + abs(y - oy)
            # Prefer smaller (d1 - 0.5*d2). Also slightly prefer closer to our side centerline.
            side = abs(x - (w - 1) // 2) + abs(y - (h - 1) // 2)
            key = (d1 - 0.5 * d2 + 0.03 * side, d1, d2, x, y)
            if best_key is None or key < best_key:
                best_key = key
                best = (x, y)
        target = best

    tx, ty = target
    # Choose move that minimizes distance to target; tie-break by dx,dy order for determinism
    best_move = None
    best_dist = None
    best_tiebreak = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        dist = abs(tx - nx) + abs(ty - ny)
        tb = (dist, abs(dx) + abs(dy), dx, dy)
        if best_dist is None or tb < best_tiebreak:
            best_dist = dist
            best_move = (dx, dy)
            best_tiebreak = tb

    return [int(best_move[0]), int(best_move[1])]