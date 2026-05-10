def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles if inb(x, y))

    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    my_set = set((x, y) for x, y in my_t if inb(x, y))
    op_set = set((x, y) for x, y in op_t if inb(x, y))
    un_set = set((x, y) for x, y in unclaimed if inb(x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist2(p, q):
        dx = p[0] - q[0]
        dy = p[1] - q[1]
        return dx * dx + dy * dy

    un_list = list(un_set)
    if un_list:
        un_list.sort(key=lambda p: dist2((ax, ay), p))
        un_list = un_list[:30]
    else:
        # If no unclaimed, bias toward opponent territory.
        op_list = list(op_set)
        op_list.sort(key=lambda p: dist2((ax, ay), p))
        op_list = op_list[:30]

    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        score = 0
        p = (nx, ny)

        if p in un_set:
            score += 200000
        elif p in op_set:
            score += 70000
        elif p in my_set:
            score += 1500
        else:
            score += 0

        if un_list:
            d = min(dist2(p, u) for u in un_list)
            score += -d
        else:
            if op_set:
                d = min(dist2(p, o) for o in op_list) if op_list else 0
                score += -2 * d

        # Small deterministic preference toward staying near center of our current territory.
        if my_set:
            # Use a fixed representative: lexicographically smallest my cell.
            rep = min(my_set)
            score += -0.01 * dist2(p, rep)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]