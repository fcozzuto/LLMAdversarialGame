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

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    rpos = []
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
        if inb(x, y) and (x, y) not in blocked:
            rpos.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not rpos:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            v = md(nx, ny, tx, ty)
            if bestv is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Opponent target: nearest resource
    opp_target = min(rpos, key=lambda p: (md(ox, oy, p[0], p[1]), p[0], p[1]))

    # Choose our "contested" target: any where we are closer than opponent
    contested = [p for p in rpos if md(sx, sy, p[0], p[1]) <= md(ox, oy, p[0], p[1])]
    if contested:
        target = min(contested, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        target = opp_target

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        my_d = md(nx, ny, target[0], target[1])
        # Look one step ahead for opponent: assume it moves toward its nearest resource (deterministically)
        opp_next_d = md(nx, ny, opp_target[0], opp_target[1])
        opp_d_now = md(ox, oy, opp_target[0], opp_target[1])

        # Higher is better: get closer to our target, and widen gap from opponent's likely target
        score = (-my_d) + (md(ox, oy, target[0], target[1]) - my_d) * 0.25
        score += (opp_d_now - opp_next_d) * 0.05

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]
    return best_move