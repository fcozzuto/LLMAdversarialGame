def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def step_ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not step_ok(nx, ny):
                continue
            d = max(abs(nx - tx), abs(ny - ty))
            key = (d, abs(nx - ox) > abs(sx - ox))
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue

        # pressure: prefer moves that reduce distance to opponent slightly only if it helps contest a resource
        opp_gain = - (max(abs(nx - ox), abs(ny - oy)) - max(abs(sx - ox), abs(sy - oy)))

        move_val = 0
        for rx, ry in resources:
            # resource value: prefer where we can arrive much sooner than opponent
            ourd = max(abs(rx - nx), abs(ry - ny))
            oppd = max(abs(rx - ox), abs(ry - oy))

            # discourage resources on/near opponent to avoid walking into their sweep
            sweep_pen = 0
            if abs(ry - oy) <= 0:
                sweep_pen += 4.0
            if ourd == 0:
                sweep_pen -= 8.0  # strong immediate pickup

            # contest advantage
            adv = (oppd - ourd)
            # also prefer closer-to-us so we keep collecting remaining
            closeness = -0.25 * ourd

            # center_rush adaptation: if opponent is near center, prioritize resources along the outer-to-center diagonal away from them
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_dist = abs(ox - cx) + abs(oy - cy)
            center_bias = 0.0
            if center_dist < (w + h) * 0.25:
                # push toward resources that are not too aligned with opponent direction (reduces collision likelihood)
                vx1, vy1 = (rx - nx), (ry - ny)
                vx2, vy2 = (ox - nx), (oy - ny)
                if (vx1 != 0 or vy1 != 0) and (vx2 != 0 or vy2 != 0):
                    # normalized dot sign: larger => same general direction
                    dot = vx1 * vx2 + vy1 * vy2
                    center_bias = -0.08 * dot / (max(1, abs(vx2) + abs(vy2)) * max(1, abs(vx1) + abs(vy1)))

            val = 10.0 * adv + closeness + center_bias - sweep_pen

            # if our move puts us into immediate threat of losing the resource, downweight
            if ourd > 0 and oppd <= ourd:
                val -= 6.0

            if val > move_val:
                move_val = val

        move_val += 0.6 * opp_gain

        if move_val > best_val or (move_val == best_val and (dx, dy) < tuple(best_move)):
            best_val = move_val
            best_move = [dx, dy]

    return best_move