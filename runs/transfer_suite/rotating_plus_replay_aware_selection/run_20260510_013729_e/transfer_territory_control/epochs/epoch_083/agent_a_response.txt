def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    x, y = observation.get("self_position") or [0, 0]
    x, y = int(x), int(y)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    self_set = set()
    opp_set = set()
    for p in self_t:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_set.add((int(p[0]), int(p[1])))
    for p in opp_t:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_set.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set()
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            un_set.add((int(p[0]), int(p[1])))

    targets = list(un_set) if un_set else []
    if not targets and opp_set:
        targets = list(opp_set)
    if not targets:
        targets = [(w // 2, h // 2)]

    def mindist(px, py, pts):
        bestd = None
        for tx, ty in pts:
            d = abs(tx - px) + abs(ty - py)
            if bestd is None or d < bestd:
                bestd = d
        return bestd if bestd is not None else 0

    best = None
    best_score = None
    best_move = [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    base = mindist(x, y, targets)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if (nx, ny) in blocked:
            continue
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue

        score = 0
        if (nx, ny) in un_set:
            score += 6
        elif (nx, ny) in opp_set:
            score += 9
        elif (nx, ny) in self_set:
            score += 2
        else:
            score += 1

        d = mindist(nx, ny, targets)
        score += max(-6, 6 - d)  # prefer moving closer

        # avoid stepping into opponent territory unless it reduces distance
        if (nx, ny) in opp_set and d >= base:
            score -= 4

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
            best_move = [dx, dy]

    return best_move