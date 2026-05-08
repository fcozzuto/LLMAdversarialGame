def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            elif inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        # deterministic drift: go towards the center unless blocked
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = min(moves, key=lambda m: (dist(sx + m[0], sy + m[1], cx, cy), m[0], m[1]))
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18
    opp_weight = 10.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Evaluate move by best resource we can "win" next from (advantage over opponent)
        move_best = -10**18
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Strong preference: resources where opponent is farther than us
            adv = (od - sd) * opp_weight
            # Tie-break: prefer closer to the resource once advantage is similar
            val = adv - sd
            # tiny center bias for determinism/stability
            val += -(abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)) * 0.01
            if val > move_best:
                move_best = val
        # Prefer moves that are at least as good and reduce distance to our chosen best target next
        if move_best > best_val or (move_best == best_val and (dx, dy) < best_move):
            best_val = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]