def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set()
    for c in observation.get("self_territory") or []:
        if c and len(c) >= 2:
            self_t.add((int(c[0]), int(c[1])))

    opp_t = set()
    for c in observation.get("opponent_territory") or []:
        if c and len(c) >= 2:
            opp_t.add((int(c[0]), int(c[1])))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    pref = []
    dx = ox - sx
    dy = oy - sy
    if abs(dx) >= abs(dy):
        pref.append((1 if dx > 0 else -1, 0))
        pref.append((0, 1 if dy > 0 else -1))
    else:
        pref.append((0, 1 if dy > 0 else -1))
        pref.append((1 if dx > 0 else -1, 0))
    ordered = []
    for m in pref:
        if m not in ordered:
            ordered.append(m)
    for m in moves:
        if m not in ordered:
            ordered.append(m)

    best = None
    best_score = -10**18
    for mx, my in ordered:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = abs(nx - ox) + abs(ny - oy)
        score = -d
        if (nx, ny) in opp_t:
            score += 1000
        if (nx, ny) in self_t:
            score += 50
        if mx == 0 and my == 0:
            score -= 1
        if score > best_score:
            best_score = score
            best = (mx, my)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]