def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Deterministic target selection: prefer nearest opponent territory, else nearest unclaimed, else opponent.
    target = (ox, oy)
    if opp_terr:
        best = None
        for px, py in opp_terr:
            d = abs(px - sx) + abs(py - sy)
            key = (d, py, px)
            if best is None or key < best[0]:
                best = (key, (px, py))
        target = best[1]
    elif unclaimed:
        best = None
        for px, py in unclaimed:
            d = abs(px - sx) + abs(py - sy)
            key = (d, py, px)
            if best is None or key < best[0]:
                best = (key, (px, py))
        target = best[1]

    tx, ty = target
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_to_target = abs(nx - tx) + abs(ny - ty)
        d_to_enemy = abs(nx - ox) + abs(ny - oy)

        val = 0
        if (nx, ny) in opp_terr:
            val += 500  # prioritize flipping opponent territory on entry
        elif (nx, ny) not in self_terr:
            val += 40   # take space elsewhere (likely unclaimed)
        # discourage walls/oscillation
        val += -3 * d_to_target
        val += 2 * (7 - d_to_enemy)  # move closer to opponent overall
        # slight preference to not waste time once close
        if d_to_target == 0:
            val += 200

        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move