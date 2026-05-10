def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    opp = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(opp[0]), int(opp[1])

    def to_set(obj):
        s = set()
        for c in obj or []:
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                s.add((int(c[0]), int(c[1])))
        return s

    un = to_set(observation.get("unclaimed_cells"))
    opt = to_set(observation.get("opponent_territory"))
    obst = to_set(observation.get("obstacles"))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def is_free(x, y): return inside(x, y) and (x, y) not in obst

    # Target choice: unclaimed adjacent to opponent territory (flip pressure), else nearby unclaimed, else avoid opponent.
    target = None
    best = 10**9
    for (x, y) in un:
        if ((x - 1, y) in opt) or ((x + 1, y) in opt) or ((x, y - 1) in opt) or ((x, y + 1) in opt):
            d = man(sx, sy, x, y)
            if d < best:
                best = d
                target = (x, y)
    if target is None and un:
        # Prefer cells on/near edges or generally closer to expand deterministically by minimal distance then lexicographic.
        best = 10**9
        for (x, y) in un:
            edge = (x in (0, w - 1) or y in (0, h - 1))
            d = man(sx, sy, x, y) - (2 if edge else 0)
            if d < best or (d == best and (x < target[0] if target else True)):
                best = d
                target = (x, y)
    if target is None:
        # Fallback: move to maximize distance from opponent while staying valid.
        target = (0, 0)
        # choose a deterministic corner farthest from opponent
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        far = -1
        for c in corners:
            d = man(c[0], c[1], ox, oy)
            if d > far:
                far = d
                target = c

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            continue
        dist_t = man(nx, ny, target[0], target[1])
        dist_o = man(nx, ny, ox, oy)
        # If we can get closer to opponent-owned boundary, prefer it indirectly via target.
        score = -dist_t + 0.25 * dist_o
        # Small deterministic tie-break: prefer lexicographically smaller move.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    dx, dy = best_move
    if not (-1 <= dx <= 1 and -1 <= dy <= 1):
        return [0, 0]
    return [int(dx), int(dy)]