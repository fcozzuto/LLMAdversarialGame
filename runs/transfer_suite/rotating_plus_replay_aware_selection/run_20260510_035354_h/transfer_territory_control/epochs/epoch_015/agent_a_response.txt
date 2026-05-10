def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = {(x, y) for x, y in obstacles if 0 <= x < w and 0 <= y < h}
    unclaimed = observation.get("unclaimed_cells") or []
    un = [(x, y) for x, y in unclaimed if 0 <= x < w and 0 <= y < h]
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    my_set = {(x, y) for x, y in my_t if 0 <= x < w and 0 <= y < h}
    op_set = {(x, y) for x, y in op_t if 0 <= x < w and 0 <= y < h}

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    def adj_unclaimed_count(x, y):
        c = 0
        for nx, ny in neighbors8(x, y):
            if (nx, ny) not in my_set and (nx, ny) not in op_set and (nx, ny) not in obs:
                c += 1
        return c

    def adj_op_count(x, y):
        c = 0
        for nx, ny in neighbors8(x, y):
            if (nx, ny) in op_set:
                c += 1
        return c

    # Prefer unclaimed cells adjacent to opponent territory; otherwise any unclaimed.
    target_list = []
    if un:
        for x, y in un:
            if adj_op_count(x, y) > 0:
                target_list.append((x, y))
        if not target_list:
            target_list = un

    if not target_list:
        return [0, 0]

    # Pick a deterministic target: nearest, then lexicographically.
    tx, ty = min(target_list, key=lambda p: (abs(p[0] - ax) + abs(p[1] - ay), p[0], p[1]))
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)] + [(0, 0)]
    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        is_op = (nx, ny) in op_set
        is_un = (nx, ny) not in my_set and (nx, ny) not in op_set
        d_to_target = abs(nx - tx) + abs(ny - ty)
        d_to_opp = abs(nx - ox) + abs(ny - oy)

        score = 0.0
        if is_op:
            score += 12.0
        if is_un:
            score += 4.0 - 0.25 * d_to_target
            score += 0.6 * adj_op_count(nx, ny)
            score += 0.2 * adj_unclaimed_count(nx, ny)
        else:
            score += 1.5 - 0.15 * d_to_target

        # Avoid walking into opponent too easily; still allow tactical hits via is_op.
        score -= 0.05 * d_to_opp

        if (score, dx, dy) > best:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]