def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    # Pick a target resource we are relatively closer to than the opponent.
    best_res = None
    best_val = 10**9
    for rx, ry in resources:
        v = dist((sx, sy), (rx, ry)) - 0.8 * dist((ox, oy), (rx, ry))
        # Slightly prefer safer moves by discouraging extreme corners when tied
        v += 0.01 * min(rx, w - 1 - rx, ry, h - 1 - ry)
        if v < best_val:
            best_val = v
            best_res = (rx, ry)

    rx, ry = best_res
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Evaluate next steps; chase chosen resource while avoiding giving opponent an easy line.
    best_move = (0, 0)
    best_score = 10**9
    cur_to_opp = dist((sx, sy), (ox, oy))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_self = dist((nx, ny), (rx, ry))
        d_opp = dist((ox, oy), (rx, ry))
        d_opp_next = dist((ox, oy), (nx, ny))

        score = d_self
        score -= 0.15 * (d_self - dist((sx, sy), (rx, ry)))  # prefer not to backtrack
        score += 0.05 * d_opp_next  # keep a little separation
        score += 0.02 * (cur_to_opp - dist((nx, ny), (ox, oy)))  # don't move toward opponent
        score += 0.25 * max(0, d_opp - d_self)  # if opponent is already closer, avoid enabling quick grab

        # Deterministic tie-break: prefer staying only if equal; then smaller dx,dy ordering by fixed dirs
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]