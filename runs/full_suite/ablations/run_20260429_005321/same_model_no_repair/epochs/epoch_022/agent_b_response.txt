def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def cell_free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def best_resource_score(x, y):
        if not resources:
            return 0, None
        best = (-10**18, None)
        for rx, ry in resources:
            rd = man(x, y, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources we can reach first; also prefer closer absolute distance.
            # If opponent is already closer, strongly discourage.
            score = (od - rd) * 10 - rd
            if od <= rd:
                score -= 30
            if score > best[0]:
                best = (score, (rx, ry))
        return best[0], best[1]

    # If no resources remain, chase opponent a bit while avoiding obstacles.
    if not resources:
        best = (-10**18, [0, 0])
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not cell_free(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            score = -d
            if score > best[0]:
                best = (score, [dx, dy])
        return best[1]

    cur_score, target = best_resource_score(sx, sy)

    best = (-10**18, [0, 0])
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_free(nx, ny):
            continue

        # Base: improve access to a favorable resource.
        rs, rt = best_resource_score(nx, ny)

        # If moving into/near a target resource, boost slightly.
        bonus = 0
        if target is not None:
            bonus = 6 - man(nx, ny, target[0], target[1])

        # Avoid getting too close to opponent if they can contest our resources.
        dop = man(nx, ny, ox, oy)
        contest_pen = 0
        if rt is not None:
            our_to_rt = man(nx, ny, rt[0], rt[1])
            opp_to_rt = man(ox, oy, rt[0], rt[1])
            if opp_to_rt <= our_to_rt:
                contest_pen = 8

        # Mild center bias (reduces cornering behind obstacles).
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = 0.01 * (abs(nx - cx) + abs(ny - cy))

        score = rs + bonus - 0.2 * dop - contest_pen - center_pen

        # Prefer staying if all else equal (deterministic tie-break).
        if score > best[0] or (score == best[0] and dx == 0 and dy == 0 and (best[1] != [0, 0])):
            best = (score, [dx, dy])

    return best[1]