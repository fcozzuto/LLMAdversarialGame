def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    def sqdist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    best_target = None
    best_adv = None
    if resources:
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_self = sqdist((sx, sy), (rx, ry))
            d_opp = sqdist((ox, oy), (rx, ry))
            adv = d_self - 0.8 * d_opp  # smaller is better for us (closer than opponent)
            if best_adv is None or adv < best_adv:
                best_adv = adv
                best_target = (rx, ry)
        if best_target is None:
            best_target = resources[0]
    else:
        best_target = (w // 2, h // 2)

    tx, ty = best_target
    opp = (ox, oy)

    valid_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        valid_moves.append((dx, dy, nx, ny))

    if not valid_moves:
        return [0, 0]

    best_move = None
    best_cost = None
    for dx, dy, nx, ny in valid_moves:
        d_t = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        d_o = (nx - opp[0]) * (nx - opp[0]) + (ny - opp[1]) * (ny - opp[1])
        # Encourage reaching target, but also keep distance from opponent.
        cost = 1.2 * d_t + 0.35 * (64 - min(64, d_o))  # closer opponent => higher cost
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]