def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_res = None
    best_d = 10**9
    for rx, ry in resources:
        d = man(sx, sy, rx, ry)
        if d < best_d:
            best_d = d
            best_res = (rx, ry)

    tx, ty = (best_res if best_res else ((w - 1) // 2, (h - 1) // 2))

    prefer = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    score_best = -10**18
    best_move = (0, 0)

    for dx, dy in prefer:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_to_target = man(nx, ny, tx, ty)
        d_to_opp = man(nx, ny, ox, oy)
        step_to_any_res = 1 if (nx, ny) in resources else 0
        score = (-d_to_target) + 0.05 * d_to_opp + 1000 * step_to_any_res
        if score > score_best:
            score_best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]