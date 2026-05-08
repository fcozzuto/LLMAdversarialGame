def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    turns = int(observation.get("turns_remaining", 0) or 0)
    parity = (sx + sy + turns) & 1

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose best step by scoring: being closer to a resource than opponent, while avoiding obstacles.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_best = 10**9
        opp_best = 10**9
        my_take = 0
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if sd < my_best:
                my_best = sd
            if od < opp_best:
                opp_best = od
            # immediate collection bonus if stepping onto a resource
            if nx == rx and ny == ry:
                my_take += 1

        # Prefer capturing resources sooner than opponent; also prefer parity alignment.
        score = 0
        score += 80 * my_take
        score += 20 * (opp_best - my_best)  # positive when we're closer
        score += -2 * my_best
        if ((nx + ny) & 1) != parity:
            score += -3

        # Slightly discourage moving adjacent to obstacles to reduce collision chances
        adj_obs = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in obstacles:
                adj_obs += 1
        score += -1.5 * adj_obs

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move