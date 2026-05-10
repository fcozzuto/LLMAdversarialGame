def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass

    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    elif opp_set:
        tx, ty = min(opp_set, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        tx, ty = ox, oy

    best_dx, best_dy = 0, 0
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in opp_set:
            val += 140
            # Prefer moves that reduce distance to where we can expand into their region
            val += -2 * (abs(nx - ox) + abs(ny - oy))
        elif (nx, ny) in unclaimed:
            val += 35
        elif (nx, ny) in self_set:
            val += 4
        else:
            val -= 2

        # Prefer progressing toward target (unclaimed first, else opponent)
        val += -1.5 * (abs(nx - tx) + abs(ny - ty))

        # Slight preference for staying away from obstacles by penalizing tight corners
        # (deterministic and cheap): count blocked neighbors around candidate
        block_cnt = 0
        for ax, ay in dirs:
            ex, ey = nx + ax, ny + ay
            if not (0 <= ex < w and 0 <= ey < h) or (ex, ey) in obstacles:
                block_cnt += 1
        val -= 0.3 * block_cnt

        if val > best_val or (val == best_val and (dx, dy) < (best_dx, best_dy)):
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]