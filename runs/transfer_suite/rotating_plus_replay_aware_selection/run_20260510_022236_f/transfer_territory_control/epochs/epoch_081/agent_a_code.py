def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    if not unclaimed:
        return [0, 0]

    up = int(observation.get("self_territory_count") or 0)
    op = int(observation.get("opponent_territory_count") or 0)
    behind = up < op

    def centroid(cells):
        if not cells:
            return (w // 2, h // 2)
        sx0 = 0
        sy0 = 0
        n = 0
        for x, y in cells:
            sx0 += x
            sy0 += y
            n += 1
        return (sx0 // n, sy0 // n)

    c_self = centroid(self_terr)
    c_op = centroid(op_terr)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose a target unclaimed cell deterministically.
    # If behind: prioritize unclaimed closer to opponent centroid (likely near their frontier).
    # If ahead: prioritize unclaimed closer to our centroid (safer expansion).
    ax, ay = c_op if behind else c_self
    best_t = None
    best_key = None
    for x, y in unclaimed:
        if not inb(x, y) or (x, y) in obstacles:
            continue
        d_to_cent = abs(x - ax) + abs(y - ay)
        d_to_us = abs(x - sx) + abs(y - sy)
        near_op = 0
        for ox, oy in op_terr:
            if abs(ox - x) + abs(oy - y) == 1:
                near_op = 1
                break
        key = (d_to_cent, d_to_us, -near_op, y, x) if behind else (d_to_us, d_to_cent, -near_op, y, x)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (x, y)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer reducing manhattan distance to target; slight preference for moving into our current territory cells
        # (deterministic tie-breaker via coordinates).
        dist = abs(tx - nx) + abs(ty - ny)
        in_ours = 1 if (nx, ny) in self_terr else 0
        in_ops = 1 if (nx, ny) in op_terr else 0
        # If behind, allow entering opponent territory earlier by lowering penalty for that.
        penalty = (2 if in_ops == 0 else (0 if behind else 2))
        key = (dist + penalty, -in_ours, in_ops, ny, nx)
        candidates.append((key, dx, dy))
    candidates.sort(key=lambda t: t[0])
    if not candidates:
        return [0, 0]
    return [int(candidates[0][1]), int(candidates[0][2])]