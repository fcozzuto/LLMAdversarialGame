def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)

    if not resources:
        if ox == sx:
            return [0, 1 if oy > sy else (-1 if oy < sy else 0)]
        return [1 if ox > sx else -1, 0 if oy == sy else (1 if oy > sy else -1)]

    resources = [tuple(r) for r in resources]

    def best_target_from(pos):
        best = None
        px, py = pos
        for rx, ry in resources:
            d = abs(rx - px) + abs(ry - py)
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        return best[1]

    best_move = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        newpos = (nx, ny)

        if newpos == opp:
            score = -10**9
        else:
            tgt = best_target_from(newpos)
            me_d = man(newpos, tgt)
            opp_d = man(opp, tgt)
            score = (opp_d - me_d) * 10 - me_d
            if abs(nx - ox) + abs(ny - oy) == 1:
                score -= 2  # mild safety

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]