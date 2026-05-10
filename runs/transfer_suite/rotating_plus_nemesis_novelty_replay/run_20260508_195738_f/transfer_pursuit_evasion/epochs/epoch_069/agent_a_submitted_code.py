def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    scores = observation.get("scores") or {}
    my_score = None
    op_score = None
    if isinstance(scores, dict):
        for k, v in scores.items():
            if "self" in str(k).lower() or "me" in str(k).lower() or "agent" in str(k).lower():
                my_score = v
            if "opp" in str(k).lower() or "opponent" in str(k).lower():
                op_score = v
    if my_score is None:
        try:
            my_score = int(observation.get("self_score", 0) or 0)
            op_score = int(observation.get("opponent_score", 0) or 0)
        except:
            my_score, op_score = 0, 0

    chase = (my_score >= op_score)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    best = None
    best_val = None
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        val = -d if chase else d
        if best is None or val > best_val or (val == best_val and (abs(dx) + abs(dy) < abs(best[0]) + abs(best[1]))):
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]