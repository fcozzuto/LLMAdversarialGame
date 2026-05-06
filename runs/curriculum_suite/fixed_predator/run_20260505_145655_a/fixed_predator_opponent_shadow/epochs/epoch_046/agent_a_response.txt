def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def d(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Resource selection: strongly prefer positions where we are not behind, then improve distance.
    best = None
    best_key = None
    for rx, ry in resources:
        dm = d(x, y, rx, ry)
        do = d(ox, oy, rx, ry)
        beat = dm - do  # <=0 means we are at least as close as opponent (good)
        # Key is maximized lexicographically
        # Prefer: larger "advantage" (opponent farther), smaller dm, then lexicographic (stable)
        adv = do - dm
        # Extra penalty if opponent can reach in <= dm (we likely lose timing on this resource)
        timing_pen = 0 if beat <= 0 else 50
        key = (adv - timing_pen, -dm, -do, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_move_key = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        dm2 = d(nx, ny, tx, ty)
        do2 = d(nx, ny, ox, oy)
        # Maximize: smaller distance to target; if tie, prefer being farther from opponent (safer)
        key = (-dm2, do2, -abs(tx - nx) - abs(ty - ny), -dx, -dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]