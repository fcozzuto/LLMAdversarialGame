def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    sx, sy = to_xy(observation.get("self_position"))
    ox, oy = to_xy(observation.get("opponent_position"))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        x, y = to_xy(it)
        if 0 <= x < gw and 0 <= y < gh:
            obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        x, y = to_xy(it)
        if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obstacles:
            continue

        candidate_key = None
        for r in resources:
            rd = r[1] - oy
            if rd < 0:
                rd = -rd
            our_d = manh(nx, ny, r[0], r[1])
            opp_d = manh(ox, oy, r[0], r[1])
            edge = opp_d - our_d
            key = (edge, -our_d, -rd, -r[0], -r[1])
            if candidate_key is None or key > candidate_key:
                candidate_key = key

        if candidate_key is None:
            continue
        if best_key is None or candidate_key > best_key:
            best_key = candidate_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]