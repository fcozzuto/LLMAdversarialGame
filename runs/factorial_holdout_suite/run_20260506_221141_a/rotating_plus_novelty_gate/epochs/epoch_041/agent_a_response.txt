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

    def dist(a, b, x, y):
        return abs(a - x) + abs(b - y)

    # Score favors resources we can arrive earlier; if tie, prefer farther win margin then nearer.
    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    t = int(observation.get("turn_index", 0) or 0)
    prefer_race = 1 if rem <= 6 else 0  # later game: prioritize winning races more

    best = None
    best_score = None
    for rx, ry in resources:
        cd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        win_margin = od - cd  # positive => we are closer
        closeness = -(cd + dist(sx, sy, ox, oy) * 0.001)
        # Add a small deterministic bias by turn to reduce tie oscillation
        bias = ((rx * 17 + ry * 31 + t) % 7) * 1e-4
        s = (win_margin * (2.5 if prefer_race else 1.4)) + closeness + bias
        key = (s, win_margin, -cd, -((rx * 13 + ry * 7) % 101))
        if best is None or key > best_score:
            best = (rx, ry)
            best_score = key

    tx, ty = best

    # Choose a single move that most reduces distance to target while avoiding obstacles.
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)]
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        nd = dist(nx, ny, tx, ty)
        cd = dist(sx, sy, tx, ty)
        # Prefer progress; if no progress, prefer diagonal/closer to reduce being stuck.
        progress = cd - nd
        opp_nd = dist(nx, ny, ox, oy)
        key = (progress, -nd, opp_nd * 0.01, -((dx + 2) * (dy + 2)))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move