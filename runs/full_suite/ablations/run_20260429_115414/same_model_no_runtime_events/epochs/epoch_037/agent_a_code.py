def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    if not resources:
        return [0, 0]

    rem = observation.get("remaining_resource_count")
    try:
        rem = int(rem) if rem is not None else len(resources)
    except:
        rem = len(resources)
    late = rem <= 4

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue

            # Distance to closest resource
            mind = 10**9
            for rx, ry in resources:
                d = dist(nx, ny, rx, ry)
                if d < mind:
                    mind = d
            # Prefer immediate collection
            collect_bonus = 0
            for rx, ry in resources:
                if rx == nx and ry == ny:
                    collect_bonus = 10**6
                    break

            # Avoid opponent; be more aggressive when late
            od = dist(nx, ny, ox, oy)
            opp_pen = (0 if late else 3) * (1 if od <= 1 else 0) + (0 if late else 1) * (0 if od > 1 else (2 - od))

            # Slight preference to reduce distance to opponent early (or chase when late)
            chase = (1 if late else -1) * (1.0 / (od + 1))

            score = collect_bonus - 10 * mind - 100 * opp_pen + chase
            if score > best_score:
                best_score = score
                best = [dx, dy]

    return best if best is not None else [0, 0]