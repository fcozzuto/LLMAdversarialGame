def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = (w - 1, h - 1) if (sx, sy) == (0, 0) else (0, 0)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if valid(nx, ny):
                return [mx, my]
        return [0, 0]

    best_score = None
    best_move = (0, 0)

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_res = None
        best_adv = None
        best_self_d = None

        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - self_d  # positive means we are closer than opponent

            # Slightly prioritize taking "soonest" even if advantage ties
            key = (adv, -self_d)
            if best_adv is None or key > (best_adv, best_self_d):
                best_adv = adv
                best_self_d = self_d
                best_res = (rx, ry)

        # Encourage direct pickup if we can step onto a resource
        pickup = 1 if any((rx == nx and ry == ny) for rx, ry in resources) else 0
        final_key = (pickup, best_adv, -best_self_d)

        if best_score is None or final_key > best_score:
            best_score = final_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]