def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best_move = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            our_d_to_best = None
            best_adv = -10**9
            for rx, ry in resources:
                our_d = abs(rx - nx) + abs(ry - ny)
                opp_d = abs(rx - ox) + abs(ry - oy)
                adv = opp_d - our_d  # positive => we can arrive earlier
                if adv > best_adv or (adv == best_adv and (our_d < our_d_to_best)):
                    best_adv = adv
                    our_d_to_best = our_d
            # Prefer winning/denying resources; tie-break toward smaller distance and stable move order
            score = (our_d_to_best if our_d_to_best is not None else 10**9) - 4 * best_adv
            if score < best_move[0]:
                best_move = (score, dx, dy)
        return [int(best_move[1]), int(best_move[2])]

    # No resources: move toward center while keeping away from opponent
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        center_d = abs(nx - cx) + abs(ny - cy)
        opp_d = abs(nx - ox) + abs(ny - oy)
        score = center_d - 0.2 * opp_d
        if score < best_move[0]:
            best_move = (score, dx, dy)
    return [int(best_move[1]), int(best_move[2])]