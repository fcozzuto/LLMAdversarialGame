def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp.add((x, y))

    candidates = []
    unclaimed = observation.get("unclaimed_cells") or []
    for p in unclaimed:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) in obstacles:
                continue
            # prefer cells that touch opponent territory (likely to flip on entry)
            touch = 0
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) in opp:
                        touch += 1
            if touch:
                candidates.append(((touch * 1000) - max(abs(x - sx), abs(y - sy)), x, y))

    # If no frontier targets, press near opponent position directly
    if not candidates:
        ox, oy = map(int, observation.get("opponent_position", (w - 1, h - 1)))
        candidates = [(0 - max(abs(ox - sx), abs(oy - sy)), ox, oy)]

    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    _, tx, ty = candidates[0]

    step_dx = 0 if tx == sx else (1 if tx > sx else -1)
    step_dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + step_dx, sy + step_dy
    if (nx, ny) in obstacles:
        # deterministically try alternate axis to avoid obstacle
        for ax_dx, ax_dy in ((step_dx, 0), (0, step_dy), (step_dx, -step_dy), (-step_dx, step_dy)):
            rx, ry = sx + ax_dx, sy + ax_dy
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                return [int(ax_dx), int(ax_dy)]
        return [0, 0]
    return [int(step_dx), int(step_dy)]