def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) and ("purs" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def neigh_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        ncnt = neigh_count(nx, ny)

        if is_evader:
            score = dist2 * 10 + ncnt
            # small bias to avoid getting stuck on edges/corners
            score += (nx > 0) + (nx < w - 1) + (ny > 0) + (ny < h - 1)
        else:
            score = -dist2 * 10 + ncnt
            # small bias to head roughly toward opponent
            score += (1 if (nx - sx) * (ox - sx) >= 0 else 0) + (1 if (ny - sy) * (oy - sy) >= 0 else 0)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # deterministic tie-break: prefer smaller |dx| then smaller |dy|
            if abs(dx) < abs(best_move[0]) or (abs(dx) == abs(best_move[0]) and abs(dy) < abs(best_move[1])):
                best_move = [dx, dy]

    return best_move