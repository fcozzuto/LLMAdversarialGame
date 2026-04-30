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

    def dist(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    t = int(observation.get("turn_index") or 0)
    rem = int(observation.get("remaining_resource_count") or 0)
    late = 1 if (t >= 48 or rem <= 5) else 0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        if resources:
            md = 10**9
            md2 = 10**9
            for rx, ry in resources:
                d = dist(nx, ny, rx, ry)
                if d < md:
                    md2 = md
                    md = d
                elif d < md2:
                    md2 = d
            score += (200 - 20 * md) + (10 if md2 < 3 else 0)
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score += -dist(nx, ny, cx, cy)

        opp_d = dist(nx, ny, ox, oy)
        score += (-5 if late else -2) * (10 - min(10, opp_d))  # prefer staying away a bit

        if dx == 0 and dy == 0:
            score -= 1  # nudge to move
        if (dx == -1 and dy == 0) or (dx == 0 and dy == -1) or (dx == 0 and dy == 1) or (dx == 1 and dy == 0) or (dx == 1 and dy == 1):
            score += 0  # deterministic no-op

        if score > best_val:
            best_val = score
            best_move = [dx, dy]

    return best_move if ok(sx + best_move[0], sy + best_move[1]) else [0, 0]