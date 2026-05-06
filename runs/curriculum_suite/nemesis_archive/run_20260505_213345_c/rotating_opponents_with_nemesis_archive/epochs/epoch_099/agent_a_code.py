def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist8(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18
    best_tiebreak = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my = (nx, ny)
        opp = (ox, oy)

        # Maximize "capture advantage": how much closer I am than opponent.
        move_best_adv = -10**18
        move_best_myd = 10**9
        move_best_opd = 10**9
        for r in resources:
            opd = dist8(opp, r)
            myd = dist8(my, r)
            adv = opd - myd
            if adv > move_best_adv or (adv == move_best_adv and (myd < move_best_myd or (myd == move_best_myd and opd < move_best_opd))):
                move_best_adv = adv
                move_best_myd = myd
                move_best_opd = opd

        # Encourage progress while keeping advantage as primary.
        move_score = move_best_adv * 1000 - move_best_myd
        tiebreak = move_best_myd * 10 + (0 if move_best_adv >= 0 else 1)
        if move_score > best_score or (move_score == best_score and tiebreak < best_tiebreak):
            best_score = move_score
            best_tiebreak = tiebreak
            best_move = [dx, dy]

    return best_move