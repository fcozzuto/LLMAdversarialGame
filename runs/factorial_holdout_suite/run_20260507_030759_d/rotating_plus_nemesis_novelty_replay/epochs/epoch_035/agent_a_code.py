def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if len(moves) != 9:
        moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(x, y):
        x = x if 0 <= x < w else sx
        y = y if 0 <= y < h else sy
        return x, y

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def near_block_pen(p):
        x, y = p
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 2
        return pen

    remaining = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    risk = 6 if remaining <= 6 else 2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        sp2 = (nx, ny)

        # One-step race evaluation: prefer moves that make some resource strictly "safer" than opponent.
        # Also add a small attraction toward high "race margin" and reduce moving away from nearest contested point.
        vals = []
        for r in resources:
            sd = man(sp2, r)
            od = man((ox, oy), r)
            margin = (od - sd)  # positive => we are closer (or tie-better)
            vals.append((margin, -sd))
        # Deterministic aggregate: take max margin, then among equal margins take smallest sd.
        vals.sort(key=lambda t: (-t[0], t[1]))
        margin, negsd = vals[0]
        closest_sd = -negsd

        # Tie-break: penalize standing adjacent to obstacles and favor slightly faster progress when margins tie.
        val = margin * 50 - closest_sd - risk * near_block_pen(sp2)

        # If opponent can grab a nearby resource immediately, discourage moves that allow it.
        opp_immediate = 0
        for r in resources:
            if man((ox, oy), r) <= 1:
                # if we are also close enough after move to race poorly, reduce
                if man(sp2, r) >= man((ox, oy), r):
                    opp_immediate += 1
        val -= 8 * opp_immediate

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]