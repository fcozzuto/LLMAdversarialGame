def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist8(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    # Choose a target we can reach sooner than the opponent, with tie-breaks for safety/positioning.
    best = None
    for r in resources:
        dm = dist8((sx, sy), r)
        do = dist8((ox, oy), r)
        # Beat them first; prefer targets not on opponent's exact row/col; prefer closer and more "central".
        beat = do - dm
        rowcol = (1 if r[1] != oy else 0) + (1 if r[0] != ox else 0)
        center = - (abs(r[0] - (w - 1) / 2.0) + abs(r[1] - (h - 1) / 2.0))
        val = (beat, rowcol, -dm, center, -r[0], -r[1])
        if best is None or val > best[0]:
            best = (val, r)
    target = best[1]

    # If we can move onto a resource, prioritize it.
    adj_resources = set(resources)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        on_res = 1 if (nx, ny) in adj_resources else 0
        d_to_t = dist8((nx, ny), target)
        d_to_o = dist8((nx, ny), (ox, oy))
        # Prefer immediate capture; otherwise reduce distance to target and keep some distance from opponent.
        score = (on_res, -d_to_t, d_to_o, -abs(nx - target[0]) - abs(ny - target[1]), -dx, -dy)
        candidates.append((score, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]