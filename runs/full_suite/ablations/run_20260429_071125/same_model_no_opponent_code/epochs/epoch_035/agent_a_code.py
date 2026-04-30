def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
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

    def clamp_move(x, y):
        if (x, y) in obstacles:
            return None
        return (x, y)

    best_t = None
    best_v = None
    for tx, ty in resources:
        ds = manh(sx, sy, tx, ty)
        do = manh(ox, oy, tx, ty)
        v = ds - 0.45 * do
        if best_v is None or v < best_v or (v == best_v and (tx, ty) < best_t):
            best_v = v
            best_t = (tx, ty)

    tx, ty = best_t
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    best_step = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # prefer moves that reduce distance to target; also discourage letting opponent get closer
        ns = manh(nx, ny, tx, ty)
        no = manh(ox, oy, tx, ty)
        # small tie-breakers: keep within bounds already; prefer moving closer to target and slightly away from obstacles
        obst_pen = 0
        for ax, ay in ((nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1), (nx + 1, ny + 1), (nx + 1, ny - 1), (nx - 1, ny + 1), (nx - 1, ny - 1)):
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                obst_pen += 0.25
        # if opponent is very near the target, prioritize exact interception by minimizing ds-no comparison
        score = (ns - 0.60 * no) + obst_pen
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_step):
            best_score = score
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]