def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def d(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = -10**18
    best = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        my_pos = (nx, ny)

        # Evaluate grabbing some resource next/soon: maximize advantage over opponent (fewer turns to that resource)
        cur_best = -10**18
        for rx, ry in resources:
            res = (rx, ry)
            my_dist = d(my_pos, res)
            opp_dist = d((ox, oy), res)

            # Prefer states where we can arrive strictly earlier; otherwise still prefer best we can do.
            # Slightly penalize longer my_dist to reduce dithering.
            advantage = opp_dist - my_dist
            val = advantage * 100 - my_dist

            # If opponent and we are equal distance, prefer closer position and central-ish bias via my_dist only.
            if advantage == 0:
                val -= 5

            if val > cur_best:
                cur_best = val

        if cur_best > best_score:
            best_score = cur_best
            best = [dx, dy]

    return best