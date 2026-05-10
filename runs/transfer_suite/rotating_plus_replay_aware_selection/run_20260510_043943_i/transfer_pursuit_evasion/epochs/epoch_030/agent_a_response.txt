def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "guard", "pursuit")) or ("evader" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs8 = moves
    def neighbor_free(x, y):
        cnt = 0
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cnt += 1
        return cnt

    def dist2(x, y):
        ddx = x - ox
        ddy = y - oy
        return ddx * ddx + ddy * ddy

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny)
        nf = neighbor_free(nx, ny)
        # Deterministic tie-break: lexicographic on move
        move_key = (dx, dy)
        if is_pursuer:
            # Get closer while avoiding tight traps
            score = (-d, -(3 - min(nf, 3)))
        else:
            # Run away; prefer open areas and anti-stuck behavior
            score = (d, min(nf, 3))
        candidates.append((score, move_key, [dx, dy]))

    if not candidates:
        return [0, 0]

    # Choose max for pursuer on primary term (-d minimized); for evader maximize d
    if is_pursuer:
        # score[0] is -d, so max means closer; also maximize second term implicitly
        best = max(candidates, key=lambda t: (t[0][0], t[0][1], -t[1][0], -t[1][1]))
    else:
        best = max(candidates, key=lambda t: (t[0][0], t[0][1], -t[1][0], -t[1][1]))
    return best[2]