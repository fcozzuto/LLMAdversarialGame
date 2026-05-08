def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def pos(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return int(p[0]), int(p[1])
        return None

    def as_xy_list(items):
        out = []
        for it in items or []:
            p = pos(it)
            if not p:
                continue
            x, y = p
            if 0 <= x < w and 0 <= y < h:
                out.append((x, y))
        return out

    s = pos(observation.get("self_position", [0, 0])) or (0, 0)
    o = pos(observation.get("opponent_position", [0, 0])) or (0, 0)
    sx, sy = s
    ox, oy = o

    obs = set(as_xy_list(observation.get("obstacles", []) or []))
    resources = as_xy_list(observation.get("resources", []) or [])
    resources = [p for p in resources if p not in obs]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if resources:
        tx, ty = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = - (abs(tx - nx) + abs(ty - ny))
            score += 0.01 * (abs(ox - nx) + abs(oy - ny))
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: deterministic maximize distance from opponent
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = abs(ox - nx) + abs(oy - ny)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]