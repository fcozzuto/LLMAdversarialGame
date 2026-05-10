def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    res = [(int(r[0]), int(r[1])) for r in resources if (int(r[0]), int(r[1])) not in obstacles]
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # For this candidate move, consider the single "most winnable" resource.
        cand = -10**18
        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive if we are closer than opponent
            # Primary: maximize advantage; Secondary: minimize our distance; Tertiary: deterministic id
            val = adv * 1000 - sd * 10 - ((rx * 17 + ry * 31) % 997) * 0.001
            if val > cand:
                cand = val

        if cand > best_val:
            best_val = cand
            best_move = (dx, dy)

    # If all candidates are bad (opponent always closer), still go toward the closest resource to avoid passivity.
    if best_val < -200:
        closest = None
        closest_d = 10**9
        for rx, ry in res:
            d = man(sx, sy, rx, ry)
            if d < closest_d:
                closest_d = d
                closest = (rx, ry)
        rx, ry = closest
        dx = 0 if rx == sx else (1 if rx > sx else -1)
        dy = 0 if ry == sy else (1 if ry > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]

    return [int(best_move[0]), int(best_move[1])]