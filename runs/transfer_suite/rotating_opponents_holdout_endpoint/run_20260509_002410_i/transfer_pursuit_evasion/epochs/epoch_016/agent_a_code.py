def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    pursuing = (("pur" in self_role) or ("chase" in self_role) or ("pursu" in self_role)) and ("evad" not in self_role)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def manh(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # If can't move anywhere (rare), stay.
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # 2-ply heuristic: my move, then assume opponent moves greedily to their objective.
    # Deterministic tie-break: smaller (abs(dx), abs(dy), dx, dy) first.
    def opp_best(nx, ny):
        opp_cand = []
        for adx, ady in moves:
            tx, ty = ox + adx, oy + ady
            if legal(tx, ty):
                # Opponent's objective opposite of mine when roles are complementary.
                # If I'm pursuer: opponent evades => maximize my distance.
                # If I'm evader: opponent pursues => minimize my distance.
                d = manh(nx, ny, tx, ty)
                score = d if pursuing else -d
                opp_cand.append((score, adx, ady, tx, ty))
        if not opp_cand:
            opp_cand = [(manh(nx, ny, ox, oy) if pursuing else -manh(nx, ny, ox, oy), 0, 0, ox, oy)]
        # Max score for both cases because score already oriented for opponent.
        opp_cand.sort(key=lambda t: (-t[0], abs(t[1]), abs(t[2]), t[1], t[2]))
        return opp_cand[0][3], opp_cand[0][4]

    best = None
    for dx, dy, nx, ny in cand:
        tx, ty = opp_best(nx, ny)
        d = manh(nx, ny, tx, ty)
        # My objective: if pursuing, minimize distance to opponent after opponent moves.
        # If evading, maximize distance.
        score = -d if pursuing else d

        # Extra shaping vs obstacles: avoid being adjacent to many obstacle blocks (potential trap).
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if inb(px, py) and (px, py) in obstacles:
                    adj_pen += 1
        score -= 0.05 * adj_pen if pursuing else -0.02 * adj_pen

        key = (-score, abs(dx), abs(dy), dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]