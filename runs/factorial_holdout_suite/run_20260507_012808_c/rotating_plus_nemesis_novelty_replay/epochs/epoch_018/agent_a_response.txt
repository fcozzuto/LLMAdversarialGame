def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        if 0 <= ox < w and 0 <= oy < h and (ox, oy) not in obstacles:
            resources = [(ox, oy)]
        else:
            resources = [(sx, sy)]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def eval_pos(nx, ny):
        my_to_opp = abs(nx - ox) + abs(ny - oy)
        best = -10**9
        for rx, ry in resources:
            md = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            if md == 0:
                return 10**6 - my_to_opp
            # Prefer resources we can reach no later than opponent, otherwise still move toward those that reduce the lead gap.
            lead = od - md  # positive means we are closer
            sc = (200 * lead) - (5 * md) - (0.1 * my_to_opp)
            if lead < 0:
                sc -= 50 * (-lead)
            if sc > best:
                best = sc
        return best

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        sc = eval_pos(nx, ny)
        if best_score is None or sc > best_score:
            best_score = sc
            best_move = [dx, dy]
    return best_move