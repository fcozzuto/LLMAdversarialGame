def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def clamp_pos(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    if not resources:
        # No resources: move away from opponent if possible
        dx = 0
        dy = 0
        if sx < ox: dx = -1
        elif sx > ox: dx = 1
        if sy < oy: dy = -1
        elif sy > oy: dy = 1
        nx, ny = clamp_pos(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            return [0, 0]
        return [dx, dy]

    # Pick resource that we can reach earlier than opponent, weighted by advantage.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        adv = do - ds
        key = (adv, -ds, -abs(rx - ox) - abs(ry - oy))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    target_dx = 0 if tx == sx else (1 if tx > sx else -1)
    target_dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    # Prefer moving directly toward target, then other nearby moves deterministically.
    ordered = [
        (target_dx, target_dy), (target_dx, 0), (0, target_dy),
        (target_dx, -target_dy), (-target_dx, target_dy),
        (1, 1), (1, 0), (1, -1), (0, 1), (0, 0), (0, -1), (-1, 1), (-1, 0), (-1, -1)
    ]
    seen = set()
    for dx, dy in ordered:
        if (dx, dy) in seen: 
            continue
        seen.add((dx, dy))
        candidates.append((dx, dy))

    def dist_after(dx, dy):
        nx, ny = clamp_pos(sx + dx, sy + dy)
        return abs(tx - nx) + abs(ty - ny), abs(ox - nx) + abs(oy - ny)

    best_move = (0, 0)
    best_score = None
    for dx, dy in candidates:
        nx, ny = clamp_pos(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        d1, d2 = dist_after(dx, dy)
        # Primary: reduce distance to target; Secondary: keep away from opponent.
        score = (-(d1), d2)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]