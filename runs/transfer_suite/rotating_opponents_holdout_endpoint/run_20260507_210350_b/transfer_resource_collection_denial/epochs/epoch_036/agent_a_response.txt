def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Fallback when no resources visible: head to farthest corner in our direction.
    if not resources:
        tx = w - 1 if sx <= w // 2 else 0
        ty = h - 1 if sy <= h // 2 else 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Race heuristic: maximize distance advantage over opponent for the best target.
    # Secondary: prefer closer-to-target and moving toward dense resource area on our half.
    my_half = sx < w // 2
    half_bias = 1 if my_half else -1

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        best_adv = -10**18
        best_d = 10**9
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            adv = d_opp - d_self
            if adv > best_adv or (adv == best_adv and d_self < best_d):
                best_adv = adv
                best_d = d_self
        # Encourage taking resources immediately and positioning for next few turns.
        # also bias x-direction towards our half to avoid mirrored traps.
        local_density = 0
        for rx, ry in resources:
            if man(nx, ny, rx, ry) <= 2:
                local_density += 1
        score = (best_adv * 1000) - (best_d * 10) + (half_bias * (nx - sx)) + (local_density * 3)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]