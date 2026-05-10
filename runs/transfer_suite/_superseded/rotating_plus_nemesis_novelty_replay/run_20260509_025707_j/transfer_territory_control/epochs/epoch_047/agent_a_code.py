def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = observation.get("resources") or []
    res = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.add((p[0], p[1]))

    opp_ter = observation.get("opponent_territory") or []
    opp_set = set()
    for p in opp_ter:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_set.add((p[0], p[1]))

    unclaimed_list = observation.get("unclaimed_cells") or []
    unclaimed = set()
    for p in unclaimed_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((p[0], p[1]))

    cx, cy = w // 2, h // 2
    if opp_set:
        ox = sum(x for x, _ in opp_set) / len(opp_set)
        oy = sum(y for _, y in opp_set) / len(opp_set)
        tx, ty = int(ox + 0.5), int(oy + 0.5)
    else:
        tx, ty = cx, cy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = -10**18
    best_move = (0, 0)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d = abs(tx - nx) + abs(ty - ny)
        score = -d

        if (nx, ny) in res:
            score += 2000
        if (nx, ny) in unclaimed:
            score += 600
        if (nx, ny) in opp_set:
            score += 1500

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score, best_move = score, (dx, dy)

    return [best_move[0], best_move[1]]