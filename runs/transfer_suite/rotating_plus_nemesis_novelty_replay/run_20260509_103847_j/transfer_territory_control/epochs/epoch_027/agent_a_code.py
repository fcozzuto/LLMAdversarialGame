def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    center_bonus = -1.5

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    # Prefer moving toward either (a) nearest unclaimed, (b) opponent territory (to flip), while keeping central control.
    target_un = None
    if unT:
        # deterministic: tie-break by x then y
        un_list = list(unT)
        un_list.sort(key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        target_un = un_list[0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue

        score = 0.0

        md_center = abs(nx - cx) + abs(ny - cy)
        score += center_bonus * md_center

        if (nx, ny) in opT:
            # Flipping is valuable; weight it strongly.
            score += 120.0
            # Also reduce distance to opponent while taking their cells.
            score += 0.5 * (abs(ox - ny) + abs(oy - nx)) * -1.0

        if (nx, ny) in unT:
            score += 60.0
        elif (nx, ny) in selfT:
            score += 10.0

        if target_un is not None:
            score += 2.0 * (abs(target_un[0] - sx) + abs(target_un[1] - sy) - (abs(target_un[0] - nx) + abs(target_un[1] - ny)))
        else:
            # If no unclaimed known, push toward opponent territory or center.
            if opT:
                op_list = list(opT)
                op_list.sort(key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
                tx, ty = op_list[0]
                score += 1.8 * (abs(tx - sx) + abs(ty - sy) - (abs(tx - nx) + abs(ty - ny)))
            score += 0.3 * (abs(ox - sx) + abs(oy - sy) - (abs(ox - nx) + abs(oy - ny)))

        # Avoid running directly into opponent territory swarm: keep a small buffer distance if not capturing.
        if (nx, ny) not in opT:
            score -= 0.15 * (abs(nx - ox) + abs(ny - oy))

        if score > best_score or (score == best_score and [dx, dy] < best_move):
            best_score = score
            best_move = [dx, dy]

    # If all moves blocked, stay.
    return best_move if best_move is not None else [0, 0]