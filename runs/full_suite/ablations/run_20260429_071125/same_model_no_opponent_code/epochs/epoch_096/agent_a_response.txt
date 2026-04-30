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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Generate candidate moves (9 including stay)
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            moves.append((dx, dy))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Score next state by (1) reaching a resource advantageously, else (2) cutting off opponent via contested resources, else (3) drift to centerline
    center = (w // 2, h // 2)
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        score = 0

        if resources:
            # Prefer resources where we would be closer than opponent; stronger if we can "beat" on the next step distance.
            best_res_score = -10**18
            for t in resources:
                us = man((nx, ny), t)
                os = man((ox, oy), t)
                # Advantage: positive if we are closer; add larger reward if we can arrive in fewer moves.
                adv = os - us
                # Encourage collecting closer resources while discouraging giving opponent the race.
                cand = adv * 30 - us * 2
                # Additional tie-break: prefer resources toward our side of the board to avoid long detours.
                cand -= abs(t[0] - sx) + abs(t[1] - sy)
                if cand > best_res_score:
                    best_res_score = cand
            score += best_res_score
        else:
            score += -(man((nx, ny), center))

        # Contest soft-block: move to reduce distance difference to opponent (makes races harder for them).
        score += (man((ox, oy), center) - man((nx, ny), center)) * 0.5

        # Slight penalty for moving away from immediate nearest resource to keep motion purposeful when advantage is unclear.
        if resources:
            closest = resources[0]
            d0 = man((sx, sy), closest)
            for r in resources[1:]:
                dr = man((sx, sy), r)
                if dr < d0:
                    d0, closest = dr, r
            score -= man((nx, ny), closest) * 0.2

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If chosen move is invalid, engine keeps us; but we only choose from valid moves anyway.
    return [int(best_move[0]), int(best_move[1])]