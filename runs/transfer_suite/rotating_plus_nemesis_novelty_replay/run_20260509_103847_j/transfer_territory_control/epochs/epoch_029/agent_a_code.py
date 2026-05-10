def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = [0, 0]
    best_score = -10**18

    # Deterministic: tie-break by (score desc, abs(dx), abs(dy), dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_op = abs(nx - ox) + abs(ny - oy)
        d_c = abs(nx - cx) + abs(ny - cy)
        d_own = abs(nx - sx) + abs(ny - sy)

        if (nx, ny) in opT:
            cell_score = 60
        elif (nx, ny) in unT:
            cell_score = 24
        elif (nx, ny) in selfT:
            cell_score = 6
        else:
            cell_score = 10

        # Prefer pushing toward opponent while keeping some central presence.
        # Also discourage unnecessary wandering.
        score = cell_score - 1.2 * d_op - 0.25 * d_c - 0.05 * d_own
        if (nx, ny) in opT:
            score += 0.15 * (abs(sx - ox) + abs(sy - oy) - d_op)  # slightly more if closing

        key = (score, -abs(dx), -abs(dy), -dx, -dy)
        best_key = (best_score, None, None, None, None)
        if score > best_score or (score == best_score and (abs(dx), abs(dy), dx, dy) < (abs(best[0]), abs(best[1]), best[0], best[1])):
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]