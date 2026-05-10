def choose_move(observation):
    sx, sy = observation["self_position"]
    px, py = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    cx, cy = (w // 2 - 1, h // 2 - 1)
    tx2, ty2 = (w // 2, h // 2)
    target = (cx, cy) if abs(cx - sx) + abs(cy - sy) <= abs(tx2 - sx) + abs(ty2 - sy) else (tx2, ty2)

    if unclaimed:
        best = None
        bestv = 10**9
        for ux, uy in unclaimed:
            d = abs(ux - sx) + abs(uy - sy)
            v = d + 0.35 * (abs(ux - target[0]) + abs(uy - target[1]))
            if v < bestv:
                bestv = v
                best = (ux, uy)
        if best is not None:
            target = best
    else:
        # If nothing to claim, try to move toward a likely flip near center
        if opp_t:
            best = None
            bestv = 10**9
            for ox, oy in opp_t:
                d = abs(ox - sx) + abs(oy - sy)
                v = d - 0.2 * (4 - (abs(ox - target[0]) + abs(oy - target[1])))
                if v < bestv:
                    bestv = v
                    best = (ox, oy)
            if best is not None:
                target = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dtarget = abs(nx - target[0]) + abs(ny - target[1])
        dopp = abs(nx - px) + abs(ny - py)
        immediate = 0.0
        if (nx, ny) in unclaimed:
            immediate += 2.2
        elif (nx, ny) in opp_t:
            immediate += 5.0
        elif (nx, ny) in self_t:
            immediate += 0.5

        # Mild preference: progress to target, keep some distance from opponent
        score = (-1.2 * dtarget) + (0.05 * dopp) + immediate
        # Deterministic tiebreak: earlier move order wins naturally via strict '>'
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]