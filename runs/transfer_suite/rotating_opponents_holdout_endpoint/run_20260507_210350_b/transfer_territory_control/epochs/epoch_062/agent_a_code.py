def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_t.add((x, y))

    targets = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))

    if not targets:
        for p in observation.get("unclaimed_cells") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in opp_t:
                    targets.append((x, y))

    if not targets:
        targets = [(w // 2, h // 2)]

    cx, cy = targets[0]
    best_d = 10**9
    for x, y in targets:
        d = abs(x - sx) + abs(y - sy)
        if d < best_d:
            best_d = d
            cx, cy = x, y

    best = -10**18
    best_move = [0, 0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            if (nx, ny) in opp_t:
                continue

            dist_to_t = abs(cx - nx) + abs(cy - ny)
            dist_to_o = abs(ox - nx) + abs(oy - ny)
            val = -dist_to_t + 0.35 * dist_to_o

            if dist_to_t == 0:
                val += 1000
            if (nx, ny) in (observation.get("resources") or []):
                val += 200

            if val > best or (val == best and (dx, dy) < (best_move[0], best_move[1])):
                best = val
                best_move = [dx, dy]

    return best_move