def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def good_cell(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    moves_sorted = sorted(moves, key=lambda d: (d[0], d[1]))  # deterministic tie-break

    if not resources:
        # Drift toward opponent-start corner to keep pressure
        tx, ty = (w - 1, h - 1) if (sx + sy) < (ox + oy) else (0, 0)
        best = None
        best_sc = -10**18
        for dx, dy in moves_sorted:
            nx, ny = sx + dx, sy + dy
            if not good_cell(nx, ny):
                continue
            sc = -cheb(nx, ny, tx, ty)
            if sc > best_sc:
                best_sc, best = sc, [dx, dy]
        return best if best is not None else [0, 0]

    # Score each move by selecting a target resource greedily, then optimizing for winning race.
    best_move = [0, 0]
    best_score = -10**18
    for mdx, mdy in moves_sorted:
        nx, ny = sx + mdx, sy + mdy
        if not good_cell(nx, ny):
            continue

        # Choose best target for this move
        my_best = 10**9
        opp_best = 10**9
        chosen = None
        for rx, ry in resources:
            dmy = cheb(nx, ny, rx, ry)
            dob = cheb(ox, oy, rx, ry)
            # Prefer resources where we can arrive no later than opponent; tie by earlier arrival and farther from opponent.
            lex = (0 if dmy <= dob else 1, dmy, -dob, rx, ry)
            if chosen is None or lex < chosen[0]:
                chosen = (lex, dmy, dob)
        _, dmy, dob = chosen

        # Main objective: improve advantage; slight preference for closer resources to reduce future uncertainty.
        my_best = dmy
        opp_best = dob
        score = (opp_best - my_best) * 100 - my_best * 3

        # Secondary: if landing on a resource, boost decisively.
        if (nx, ny) in resources:
            score += 10**6

        # Tertiary: avoid stepping into positions that are "dead" relative to opponent (they can capture much sooner).
        if my_best > 0 and opp_best + 0 <= my_best - 2:
            score -= 50

        if score > best_score:
            best_score = score
            best_move = [mdx, mdy]

    return best_move