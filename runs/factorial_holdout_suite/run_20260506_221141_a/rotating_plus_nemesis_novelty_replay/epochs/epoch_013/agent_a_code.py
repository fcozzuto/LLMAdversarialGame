def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))
    obs_list = observation.get("obstacles", []) or []
    obs = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    res_list = observation.get("resources", []) or []
    resources = []
    for r in res_list:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_target = None
    best_score = None
    for rx, ry in resources:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        # Prefer close targets for self, but avoid ones opponent can reach much faster
        score = sd + (10 if od + 1 < sd else 0) + (0 if od >= sd else 2 * (sd - od))
        if best_score is None or score < best_score or (score == best_score and (rx, ry) < best_target):
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target
    chosen = None
    chosen_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = manh(nx, ny, tx, ty)
        od = manh(ox, oy, tx, ty)
        # Slightly prefer moving to reduce distance while not letting opponent advantage grow
        score = dist + (3 if od + 1 < dist else 0)
        if chosen_score is None or score < chosen_score or (score == chosen_score and (dx, dy) < chosen):
            chosen_score = score
            chosen = (dx, dy)

    if chosen is None:
        return [0, 0]
    return [int(chosen[0]), int(chosen[1])]