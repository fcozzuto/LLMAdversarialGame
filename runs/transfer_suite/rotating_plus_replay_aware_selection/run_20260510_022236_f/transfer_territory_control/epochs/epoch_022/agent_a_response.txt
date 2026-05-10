def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    if not unclaimed:
        return [0, 0]

    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_center_bias = 0
    for p in (observation.get("opponent_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            if int(p[0]) == w // 2 and int(p[1]) == h // 2:
                opp_center_bias = 1
                break

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    center = (w // 2, h // 2)

    # candidate score: adjacent-to-our, closer to center, then closer to us
    best = None
    for p in unclaimed:
        if not (isinstance(p, (list, tuple)) and len(p) >= 2):
            continue
        tx, ty = int(p[0]), int(p[1])
        if not inb(tx, ty) or (tx, ty) in obstacles:
            continue
        adj = 0
        if self_terr:
            for dd in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                if (tx - dd[0], ty - dd[1]) in self_terr:
                    adj = 1
                    break
        dc = abs(tx - center[0]) + abs(ty - center[1])
        d0 = abs(tx - sx) + abs(ty - sy)
        # if opponent is already center-claiming, weight center less to prioritize expansion
        score = (-3 * adj) + (dc * (0.6 if opp_center_bias else 0.35)) + d0
        if best is None or score < best[0]:
            best = (score, tx, ty)
    if best is None:
        return [0, 0]
    _, tx, ty = best

    # move one step toward target; ensure not into obstacle/out of bounds; else try best alternative by same heuristic
    best_step = (10**9, 0, 0)
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd0 = abs(tx - nx) + abs(ty - ny)
        ncenter = abs(nx - center[0]) + abs(ny - center[1])
        adj = 0
        if self_terr:
            for dd in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                if (nx - dd[0], ny - dd[1]) in self_terr:
                    adj = 1
                    break
        step_score = nd0 + 0.2 * ncenter - 2.5 * adj
        if step_score < best_step[0]:
            best_step = (step_score, dx, dy)

    return [int(best_step[1]), int(best_step[2])]