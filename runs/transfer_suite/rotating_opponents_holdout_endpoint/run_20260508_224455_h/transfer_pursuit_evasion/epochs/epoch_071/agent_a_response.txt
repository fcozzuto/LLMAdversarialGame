def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = str(observation.get("self_role") or observation.get("role") or "")
    is_evader = ("evad" in role.lower()) or ("escape" in role.lower())

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x", -1)), int(p.get("y", -1))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except:
            pass

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_score = None

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    parity = int(observation.get("turn_index", 0) or 0) & 1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue

        if (nx, ny) == (ox, oy) and not is_evader:
            score = 10**9
        elif (nx, ny) == (ox, oy) and is_evader:
            score = -10**9
        else:
            d = dist((nx, ny), (ox, oy))
            block = 0
            if dx != 0 and dy != 0:
                block = 1 if ((nx - dx, ny) in obs_set or (nx, ny - dy) in obs_set) else 0

            if is_evader:
                score = d * 100 + (nx * 3 + ny) + (parity - 0.5) * (dx - dy) - block * 5
            else:
                score = -d * 100 + (parity - 0.5) * (dx + dy) + block * 2

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]