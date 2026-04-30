def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index") or 0)
    rem = int(observation.get("remaining_resource_count") or len(resources) or 0)
    late = 1 if (t > 45 or rem <= 6) else 0

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            # prioritize resources with larger x+y in late game; otherwise just nearest
            target_val = None
            target_dist = 10**9
            target_xy = None
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < target_dist:
                    target_dist = d
                    target_xy = (rx, ry)
                    target_val = (rx + ry) if late else 0
                elif d == target_dist and late:
                    v = rx + ry
                    if target_xy is None or v > target_val:
                        target_xy = (rx, ry)
                        target_val = v
            dist_res = target_dist
            pr = target_val if late else 0
        else:
            dist_res = 0
            pr = 0

        dist_op = man(nx, ny, ox, oy)
        # Move toward resources, keep away from opponent, and slightly prefer high-value resources late
        score = (-dist_res) + (0.35 * dist_op) + (0.06 * pr)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]