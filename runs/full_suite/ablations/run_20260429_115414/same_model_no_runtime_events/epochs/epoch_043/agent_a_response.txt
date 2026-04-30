def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    rem = observation.get("remaining_resource_count", 0)
    try:
        rem = int(rem)
    except:
        rem = 0
    late = rem <= 4

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        if resources:
            best_res_val = None
            for rx, ry in resources:
                dme = cheb(nx, ny, rx, ry)
                dop = cheb(ox, oy, rx, ry)
                # Prefer being closer than opponent; late game prioritize "we win this race".
                if late:
                    race = (dme - dop)
                    val = race * 100 + dme
                else:
                    val = dme * 1.0 - 0.35 * dme + (dme - dop) * 0.15
                    val = val + (0 if dme <= dop else 0.6)
                if best_res_val is None or val < best_res_val:
                    best_res_val = val
            score = best_res_val
        else:
            # No visible resources: move toward opponent or center if not late.
            if late:
                score = cheb(nx, ny, ox, oy)
            else:
                cx, cy = (w - 1) // 2, (h - 1) // 2
                score = cheb(nx, ny, cx, cy)

        if best_val is None or score < best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]