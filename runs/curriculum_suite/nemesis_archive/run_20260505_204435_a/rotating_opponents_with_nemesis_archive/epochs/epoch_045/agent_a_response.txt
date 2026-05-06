def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    for r in resources:
        if isinstance(r, dict):
            p = r.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        else:
            continue
        if legal(x, y):
            targets.append((x, y))

    if not legal(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if legal(nx, ny):
                    return [dx, dy]
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    s_pos = (sx, sy)
    o_pos = (ox, oy)

    if targets:
        s_best = min(targets, key=lambda t: dist(s_pos, t))
        o_best = min(targets, key=lambda t: dist(o_pos, t))
        pursue = s_best if dist(s_pos, s_best) <= dist(o_pos, s_best) else o_best
    else:
        pursue = ((w - 1) // 2, (h - 1) // 2)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        npos = (nx, ny)

        # Heuristic: go toward pursue; if opponent threatens, add a "contest" bonus by staying farther from opponent.
        d_to = dist(npos, pursue)
        d_opp = dist(npos, o_pos)

        # Additional deterministic shaping: gently avoid steps that reduce distance for opponent to pursue too much.
        o_after = (ox, oy)
        d_opp_to = dist(o_after, pursue)
        # Approximate opponent advantage change by how close we are to the pursue compared to opponent
        opp_adv = d_opp_to - d_to  # higher means we are relatively closer

        score = (-2.2 * d_to) + (0.08 * d_opp) + (0.6 * opp_adv)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]