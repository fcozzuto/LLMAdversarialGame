def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a materially different target than pure greedy: maximize lead but also prefer shorter travel.
    if resources:
        best = None
        bestv = None
        for rx, ry in resources:
            d_me = man(sx, sy, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            if d_me == 0:
                score = 10**12
            else:
                # Encourage gaining/keeping tempo; penalize being too close to opponent.
                lead = d_opp - d_me
                opp_pressure = man(rx, ry, ox, oy)
                score = lead * 100 - d_me * 2 - opp_pressure * 0.5
            if best is None or score > bestv or (score == bestv and (rx, ry) < best):
                bestv = score
                best = (rx, ry)
        tx, ty = best
    else:
        # Endgame: move toward center while staying away from opponent.
        tx, ty = w // 2, h // 2

    # Greedy step toward target with deterministic obstacle/opp-avoidance fallback.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Primary: reduce Manhattan distance to target; Secondary: avoid stepping into opponent's vicinity.
        d1 = man(nx, ny, tx, ty)
        d2 = man(nx, ny, ox, oy)
        # Tiny deterministic tie-break: prefer moves with smaller (dx,dy) lexicographic.
        score = (-d1 * 1000) + (d2 * 3)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]