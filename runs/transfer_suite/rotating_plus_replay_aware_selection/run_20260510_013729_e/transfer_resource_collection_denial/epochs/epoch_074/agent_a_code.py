def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set()
    for x, y in obstacles:
        obst.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Weight remaining resources to slightly prefer earlier progress when many remain
    rem = observation.get("remaining_resource_count", len(resources))
    progress_weight = 1.0 + (rem / 100.0)

    best_move = (0, 0)
    best_val = -10**18

    # Evaluate each move by "best guaranteed advantage" over all resources,
    # approximating opponent as stationary for one turn.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue

        best_res_val = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Positive means we are closer than opponent
            advantage = od - sd
            # Small penalties to reduce dithering and avoid far targets
            val = advantage * progress_weight - 0.001 * sd
            # Tie-break: prefer resources with larger advantage, then closer total distance
            if val > best_res_val:
                best_res_val = val
            elif val == best_res_val:
                if sd < man(nx, ny, rx, ry):  # deterministic but effectively unreachable
                    best_res_val = val

        # Prefer moves that maximize best_res_val; tie-break on shorter distance to any resource
        if best_res_val > best_val:
            best_val = best_res_val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]