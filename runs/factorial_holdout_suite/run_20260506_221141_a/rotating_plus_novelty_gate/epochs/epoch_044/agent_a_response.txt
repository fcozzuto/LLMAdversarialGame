def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_move = [0, 0]

    def d(a, b, x, y):
        return abs(a - x) + abs(b - y)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        # For each move, aim for the resource where we gain the most "lead" vs opponent.
        move_score = None
        for rx, ry in resources:
            sd = d(nx, ny, rx, ry)
            od = d(ox, oy, rx, ry)
            # Lead first; if tied, prefer closer target.
            s = (od - sd, -sd, -d(ox, oy, sx, sy))
            move_score = s if move_score is None else (s if s > move_score else move_score)

        if move_score is None:
            continue

        # Slight bias to progress (avoid getting stuck trading ties).
        progress = d(sx, sy, sx + dx, sy + dy)
        final = (move_score[0], move_score[1] + 0.01 * progress, move_score[2])
        if best is None or final > best:
            best = final
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]