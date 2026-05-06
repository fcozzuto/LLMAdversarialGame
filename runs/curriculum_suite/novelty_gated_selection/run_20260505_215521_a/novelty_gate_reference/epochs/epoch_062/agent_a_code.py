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
    if not resources:
        return [0, 0]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    deltas.sort()

    best = None
    best_val = None

    opp_close = min(resources, key=lambda c: manh((ox, oy), c))
    opp_close_d = manh((ox, oy), opp_close)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # estimate: choose the resource that maximizes margin (opponent distance minus our distance)
        local_best = None
        local_val = -10**9
        for rx, ry in resources:
            sd = manh((nx, ny), (rx, ry))
            od = manh((ox, oy), (rx, ry))
            # Prefer taking something the opponent isn't already extremely close to
            near_opp_pen = 0
            if opp_close_d <= 2 and (rx, ry) == opp_close:
                near_opp_pen = 30
            v = (od - sd) - 0.15 * sd - 0.02 * od - near_opp_pen
            if v > local_val:
                local_val = v
                local_best = (rx, ry)

        # If opponent is close to some resource, bias toward disrupting their path: move closer to that resource
        if opp_close_d <= 2:
            d_to_opp_close = manh((nx, ny), opp_close)
            v2 = local_val - 0.1 * d_to_opp_close
        else:
            v2 = local_val

        if best_val is None or v2 > best_val or (v2 == best_val and (dx, dy) < best):
            best_val = v2
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]