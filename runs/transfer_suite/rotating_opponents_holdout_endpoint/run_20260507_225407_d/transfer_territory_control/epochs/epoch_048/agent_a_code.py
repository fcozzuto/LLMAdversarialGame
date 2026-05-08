def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                self_t.add((x, y))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                opp_t.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in self_t and (x, y) not in opp_t:
                unclaimed.add((x, y))

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    center = (w // 2, h // 2)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 8
        elif (nx, ny) in opp_t:
            score += 11
        elif (nx, ny) in self_t:
            score += 1
        else:
            score += 3

        score += max(0, 6 - md(nx, ny, center[0], center[1])) * 0.2
        score += md(nx, ny, ox, oy) * 0.15  # keep distance from opponent

        if unclaimed:
            t = min(unclaimed, key=lambda c: md(nx, ny, c[0], c[1]))
            score += max(0, 10 - md(nx, ny, t[0], t[1])) * 0.35
        elif opp_t:
            t = min(opp_t, key=lambda c: md(nx, ny, c[0], c[1]))
            score += max(0, 10 - md(nx, ny, t[0], t[1])) * 0.25
        else:
            score += max(0, 6 - md(nx, ny, center[0], center[1])) * 0.1

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    if best_score is None:
        return [0, 0]
    return best_move