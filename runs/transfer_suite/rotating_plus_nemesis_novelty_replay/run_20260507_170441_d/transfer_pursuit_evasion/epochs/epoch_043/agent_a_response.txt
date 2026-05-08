def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    pursuer = False
    if "pursuer" in self_role:
        pursuer = True
    elif "pursuer" in opp_role:
        pursuer = False
    else:
        pursuer = True

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best = None
    bestv = None
    bests = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        man = abs(nx - ox) + abs(ny - oy)
        cheb = max(abs(nx - ox), abs(ny - oy))
        v1 = -man if pursuer else man
        v2 = -cheb if pursuer else cheb
        # tiebreak: prefer moving (avoid staying) when equal
        move_pref = 0 if (dx == 0 and dy == 0) else 1
        if best is None:
            best, bestv, bests = (dx, dy), (v1, v2), move_pref
        else:
            cand_v = (v1, v2)
            if cand_v > bestv or (cand_v == bestv and move_pref > bests):
                best, bestv, bests = (dx, dy), cand_v, move_pref

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]