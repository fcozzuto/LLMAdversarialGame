def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # keep some mobility away from opponent
        best = None
        best_s = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = abs(nx - ox) + abs(ny - oy)
                if d > best_s:
                    best_s = d
                    best = (dx, dy)
        return list(best) if best is not None else [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target resource that we can reach earlier than opponent, prefer those with large margin.
    best_move = [0, 0]
    best_val = -10**18
    res_count = int(observation.get("remaining_resource_count") or len(resources))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Evaluate best resource for this next position.
        move_val = -10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Bonus if we step onto a resource now.
            step_on = 0 if d_self != 0 else 1000
            # Prefer taking resources where opponent is slower.
            margin = d_opp - d_self
            # Small bias to reduce distance among tied margins.
            focus = -d_self
            # Extra urgency when few resources remain.
            urgency = (res_count <= 4) * 5
            v = step_on + 20 * margin + focus + urgency
            if v > move_val:
                move_val = v

        # Denier response: if we can either reach a resource much sooner OR move to a position that
        # increases our distance while still allowing near-term collection, prefer it.
        dist_away = cheb(nx, ny, ox, oy)
        move_val += 0.2 * dist_away

        if move_val > best_val:
            best_val = move_val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]