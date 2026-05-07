def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18
    best_self_near = 10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Win condition proxy: after this move, maximize how much sooner we reach the best resource than the opponent.
        best_adv = -10**18
        near_self = 10**9
        for rx, ry in resources:
            d_self = manh(nx, ny, rx, ry)
            d_opp = manh(ox, oy, rx, ry)
            adv = d_opp - d_self
            if adv > best_adv:
                best_adv = adv
            if d_self < near_self:
                near_self = d_self

        # Prefer moves that secure the best advantage; tie-break by closer approach.
        if best_adv > best_score or (best_adv == best_score and (near_self < best_self_near or (near_self == best_self_near and (dx, dy) < tuple(best_move)))):
            best_score = best_adv
            best_self_near = near_self
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]