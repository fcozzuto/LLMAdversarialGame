def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            best_res_d = None
            res_on = 0
            for rx, ry in resources:
                if rx == nx and ry == ny:
                    res_on = 1
                    best_res_d = 0
                    break
                d = dist(nx, ny, rx, ry)
                if best_res_d is None or d < best_res_d:
                    best_res_d = d
            # Prefer grabbing resource, then closer to nearest, slightly discourage moving into opponent proximity
            opp_d = dist(nx, ny, ox, oy)
            score = (-100000 * res_on) + best_res_d + (0 if opp_d >= 2 else 3 - opp_d)
        else:
            # No resources: move toward opponent deterministically
            score = dist(nx, ny, ox, oy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]