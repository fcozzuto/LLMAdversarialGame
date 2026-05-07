def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for x, y in obstacles:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    best = None
    for x, y in resources:
        x, y = int(x), int(y)
        if not (0 <= x < w and 0 <= y < h) or (x, y) in obs_set:
            continue
        md = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        margin = od - md  # positive => I can arrive sooner
        # Prefer winning sooner; then shorter time; then larger advantage; then deterministic coord
        cand = (0 if margin > 0 else 1, -margin, md, x, y)
        if best is None or cand < best[0]:
            best = (cand, (x, y))
    if best is None:
        return [0, 0]

    tx, ty = best[1]
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs_set:
                continue
            md = cheb(nx, ny, tx, ty)
            od = cheb(nx, ny, ox, oy)
            dist_to_target_self = md
            dist_to_target_opp = cheb(ox, oy, tx, ty)
            # Primary: reduce distance to chosen target; Secondary: keep opponent away a bit
            # Tertiary: if tied, prefer move that also improves relative race vs opponent
            race_gain = (dist_to_target_opp - md)
            moves.append((dist_to_target_self, -race_gain, -od, dx, dy))

    if not moves:
        return [0, 0]
    moves.sort()
    return [int(moves[0][3]), int(moves[0][4])]