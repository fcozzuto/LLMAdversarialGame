def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(x), int(y)) for x, y in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx = 0 if ox >= W // 2 else W - 1
        ty = 0 if oy >= H // 2 else H - 1
        bestd, best = 10**9, (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = man(nx, ny, tx, ty)
            if d < bestd:
                bestd, best = d, (dx, dy)
        return [best[0], best[1]]

    # Evaluate candidate next positions by best guaranteed advantage
    # For each move, compute best resource "lead": (opp_d - my_d), then tie by my_d.
    best_tuple = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        best_lead = -10**9
        best_my_d = 10**9
        best_op_d = 10**9

        for rx, ry in resources:
            my_d = man(nx, ny, rx, ry)
            op_d = man(ox, oy, rx, ry)
            lead = op_d - my_d
            if lead > best_lead or (lead == best_lead and (my_d < best_my_d or (my_d == best_my_d and op_d < best_op_d))):
                best_lead, best_my_d, best_op_d = lead, my_d, op_d

        # Small extra bias: reduce risk of opponent stealing by improving closeness for the closest resource.
        # This is deterministic and cheap.
        closest_my = min(man(nx, ny, rx, ry) for rx, ry in resources)
        tup = (best_lead, -closest_my, -best_op_d, -best_my_d)
        if best_tuple is None or tup > best_tuple:
            best_tuple, best_move = tup, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]