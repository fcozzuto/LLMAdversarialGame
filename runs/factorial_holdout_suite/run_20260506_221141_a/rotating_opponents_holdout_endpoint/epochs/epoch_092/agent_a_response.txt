def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    rem = observation.get("remaining_resource_count", len(resources))
    try:
        rem = int(rem)
    except:
        rem = len(resources)

    # If many resources remain, be a bit more aggressive; late-game, focus on contest (deny).
    deny_weight = 0.25 if rem > 6 else 0.55
    self_weight = 1.0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Choose best resource under a deterministic heuristic that favors being closer than opponent.
        local_best = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we can arrive significantly earlier; slight preference to nearer resources.
            val = self_weight * (-sd) + deny_weight * ((od - sd))
            # Tie-break deterministically by coordinates to keep stable.
            if val > local_best:
                local_best = val
            elif val == local_best:
                if (rx, ry) < (0, 0):  # never true; keep structure deterministic without extra state
                    local_best = val

        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)
        elif local_best == best_val:
            # Deterministic tie-break: prefer staying still, then lexicographically smaller dx,dy.
            if best_move == (0, 0):
                continue
            if (dx, dy) == (0, 0):
                best_move = (dx, dy)
            elif (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]