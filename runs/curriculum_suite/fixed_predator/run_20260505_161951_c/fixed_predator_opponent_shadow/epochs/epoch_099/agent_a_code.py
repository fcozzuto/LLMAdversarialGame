def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def min_self_d(nx, ny):
        if not resources:
            return 10**9
        return min(md(nx, ny, rx, ry) for rx, ry in resources)

    def min_opp_d(nx, ny):
        if not resources:
            return 10**9
        return min(md(ox, oy, rx, ry) for rx, ry in resources)

    cur_self_min = min_self_d(sx, sy)
    cur_opp_min = min(md(ox, oy, rx, ry) for rx, ry in resources) if resources else 10**9

    # Determine whether we can "race" some resource advantageously this step.
    best_adv = None
    if resources:
        for rx, ry in resources:
            sd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            # Prefer resources we are at least as fast as the opponent (or better).
            if sd <= od:
                key = (adv, -sd, -od)
                if best_adv is None or key > best_adv[0]:
                    best_adv = (key, (rx, ry))
    target = best_adv[1] if best_adv else None

    best_move = None
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy

        if resources:
            next_self_min = min_self_d(nx, ny)
            next_opp_min = cur_opp_min  # opponent position unchanged within this move

            gap = next_opp_min - next_self_min  # larger is better
            # If we have a target, pull towards it strongly; otherwise also consider reducing opponent's min.
            if target:
                tx, ty = target
                tdist = md(nx, ny, tx, ty)
                cur_tdist = md(sx, sy, tx, ty)
                # Encourage moving closer to the target without sacrificing the gap.
                key = (gap, -(tdist), -(cur_tdist - tdist), -next_self_min, -dx*dx - dy*dy)
            else:
                # No clear race target: maximize gap; then minimize our distance.
                key = (gap, -next_self_min, -(abs(nx - ox) + abs(ny - oy)), -dx*dx - dy*dy)
        else:
            # No resources: head toward midpoint between agents (deterministic).
            tx, ty = (sx + ox) // 2, (sy + oy) // 2
            key = (-md(nx, ny, tx, ty), 0)

        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]