def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [int(dx), int(dy)]

    me = (sx, sy)
    opp = (ox, oy)

    # Choose a strategic target: maximize advantage (opp further), then be close to us.
    best_r = resources[0]
    best_key = (-10**9, 10**9, best_r[0], best_r[1])
    for r in resources:
        adv = man(opp, r) - man(me, r)
        key = (adv, man(me, r), r[0], r[1])
        if key[0] > best_key[0] or (key[0] == best_key[0] and key[1] < best_key[1]) or \
           (key[0] == best_key[0] and key[1] == best_key[1] and (key[2], key[3]) < (best_key[2], best_key[3])):
            best_key = key
            best_r = r

    target = best_r

    # Move selection: greedily improve our approach to target while discouraging opponent access.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        new_me = (nx, ny)
        d_us = man(new_me, target)
        d_opp = man(opp, target)
        # Slightly prefer moves that reduce distance to the best "nearby" resources too.
        near_us = min(man(new_me, r) for r in resources)
        near_opp = min(man(opp, r) for r in resources)
        score = (-d_us) + (0.35 * d_opp) + (-0.12 * near_us) + (0.10 * near_opp)
        # Tie-break deterministically toward lower dx, then lower dy magnitude.
        if score > best_score or (score == best_score and (abs(dx), abs(dy), dx, dy) < (abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]