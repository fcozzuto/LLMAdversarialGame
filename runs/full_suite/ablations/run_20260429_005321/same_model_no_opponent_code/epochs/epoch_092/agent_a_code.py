def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_dx, best_dy, best_score = 0, 0, -10**18

    targets = resources if resources else [(cx, cy)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_me = min(manh(nx, ny, tx, ty) for tx, ty in targets)
        d_to_opp = manh(nx, ny, ox, oy)
        score = -d_to_me + 0.05 * d_to_opp
        if resources and d_to_me == 0:
            score += 1000000
        if score > best_score or (score == best_score and (dx, dy) < (best_dx, best_dy)):
            best_dx, best_dy, best_score = dx, dy, score

    return [int(best_dx), int(best_dy)]